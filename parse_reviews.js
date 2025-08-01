const fs = require('fs');
const path = require('path');

function parseRelativeDate(dateString) {
    const now = new Date();
    const lower = dateString.toLowerCase();
    
    if (lower.includes('day') && lower.includes('ago')) {
        const days = parseInt(lower.match(/(\d+)\s*day/)?.[1] || '0');
        const date = new Date(now);
        date.setDate(date.getDate() - days);
        return date;
    }
    
    if (lower.includes('week') && lower.includes('ago')) {
        const weeks = parseInt(lower.match(/(\d+)\s*week/)?.[1] || '0');
        const date = new Date(now);
        date.setDate(date.getDate() - (weeks * 7));
        return date;
    }
    
    if (lower.includes('month') && lower.includes('ago')) {
        const months = parseInt(lower.match(/(\d+)\s*month/)?.[1] || '0');
        const date = new Date(now);
        date.setMonth(date.getMonth() - months);
        return date;
    }
    
    if (lower.includes('year') && lower.includes('ago')) {
        const years = parseInt(lower.match(/(\d+)\s*year/)?.[1] || '0');
        const date = new Date(now);
        date.setFullYear(date.getFullYear() - years);
        return date;
    }
    
    // Default to now if can't parse
    return now;
}

function parseReviews(textContent) {
    const lines = textContent.split('\n').map(line => line.replace(/^\s*\d+→/, '').trim());
    
    // Skip header lines and find where reviews start
    let reviewStartIndex = -1;
    for (let i = 0; i < lines.length; i++) {
        if (lines[i] === 'Bob Davies') {
            reviewStartIndex = i;
            break;
        }
    }
    
    if (reviewStartIndex === -1) {
        console.log('Could not find review start marker');
        return [];
    }
    
    const reviewLines = lines.slice(reviewStartIndex);
    const reviews = [];
    let i = 0;
    
    while (i < reviewLines.length) {
        const line = reviewLines[i];
        
        if (!line) {
            i++;
            continue;
        }
        
        // Skip owner responses
        if (line === 'New Bank Health Centre (owner)') {
            i++;
            // Skip all owner response content until we find the next reviewer
            while (i < reviewLines.length) {
                const nextLine = reviewLines[i];
                if (isLikelyReviewerName(nextLine, reviewLines, i)) {
                    break;
                }
                i++;
            }
            continue;
        }
        
        // Check if this is likely a reviewer name
        if (isLikelyReviewerName(line, reviewLines, i)) {
            const review = parseReviewBlock(reviewLines, i);
            if (review && review.text.trim()) {
                reviews.push(review);
            }
            i = review ? review.nextIndex : i + 1;
        } else {
            i++;
        }
    }
    
    // Sort by date (newest first)
    reviews.sort((a, b) => {
        if (!a.date && !b.date) return 0;
        if (!a.date) return 1;
        if (!b.date) return -1;
        return new Date(b.date) - new Date(a.date);
    });
    
    return reviews;
}

function isLikelyReviewerName(line, allLines, currentIndex) {
    if (!line || line.trim() === '') return false;
    if (/^[❤️🙏]/.test(line)) return false;
    if (line.includes('ago') && !line.includes(' ')) return false;
    if (line.includes('Local Guide')) return false;
    if (line === 'New') return false;
    if (/^\d+$/.test(line)) return false;
    if (line.includes('Photo')) return false;
    if (line.startsWith('Edited')) return false;
    if (line === 'New Bank Health Centre (owner)') return false;
    
    // Skip metadata patterns that aren't actual names
    if (/^\d+\s+reviews?$/i.test(line)) return false; // "6 reviews", "1 review"
    if (/^\d+\s+reviews?·\d+\s+photos?$/i.test(line)) return false; // "6 reviews·2 photos"
    if (line.includes('reviews') && !line.includes('Local Guide')) return false;
    if (line.includes('photos') && !line.includes('Local Guide')) return false;
    if (line.startsWith('Rating:')) return false;
    
    // Check if it's likely a reviewer name by looking at context
    // Reviewer names are usually followed by Local Guide info, date, or review text
    const nextLine = allLines[currentIndex + 1];
    const lineAfterNext = allLines[currentIndex + 2];
    
    // If next line is Local Guide info, this is likely a reviewer name
    if (nextLine && nextLine.includes('Local Guide·')) return true;
    
    // If this line looks like a person's name (not too long, reasonable format)
    // and doesn't contain review-related keywords
    if (line.length < 50 && !line.includes('…More') && !line.startsWith('Rating:')) {
        
        // Check if followed by review metadata pattern
        if (nextLine && (/^\d+\s+reviews?/i.test(nextLine) || nextLine.includes('Local Guide'))) {
            return true;
        }
        
        // Check if followed by date
        if (nextLine && (nextLine.includes('ago') || nextLine === 'New')) {
            return true;
        }
        
        // Or if followed by another line that looks like a date
        if (lineAfterNext && (lineAfterNext.includes('ago') || lineAfterNext === 'New')) {
            return true;
        }
        
        // Additional check: if it looks like a person's name (contains typical name patterns)
        if (isPersonNamePattern(line)) {
            return true;
        }
    }
    
    return false;
}

function isPersonNamePattern(text) {
    // Simple heuristics for person names:
    // - Contains spaces (first name + last name)
    // - Starts with capital letter
    // - Doesn't contain numbers unless it's a username pattern
    // - Reasonable length
    
    if (text.length > 50) return false;
    if (text.includes('…More')) return false;
    if (text.startsWith('Rating:')) return false;
    if (/reviews?|photos?/i.test(text) && !text.includes('Local Guide')) return false;
    
    // If it has spaces and starts with capital letter, likely a name
    if (/^[A-Z]/.test(text) && text.includes(' ')) {
        return true;
    }
    
    // Single word names (like usernames) starting with capital
    if (/^[A-Z][a-zA-Z0-9_]*$/.test(text) && text.length > 2) {
        return true;
    }
    
    return false;
}

function parseReviewBlock(lines, startIndex) {
    const review = {
        reviewer: lines[startIndex],
        localGuideInfo: '',
        date: null,
        dateString: '',
        text: '',
        reactions: '',
        isNew: false,
        nextIndex: startIndex + 1
    };
    
    let i = startIndex + 1;
    let foundDate = false;
    let textStarted = false;
    
    while (i < lines.length) {
        const line = lines[i];
        
        if (!line) {
            i++;
            continue;
        }
        
        // Stop if we hit another reviewer or owner response
        if (isLikelyReviewerName(line, lines, i) || line === 'New Bank Health Centre (owner)') {
            break;
        }
        
        // Local Guide info
        if (line.includes('Local Guide·') && !review.localGuideInfo) {
            review.localGuideInfo = line;
        }
        // Date info
        else if (!foundDate && (line.includes('ago') || line === 'New' || line.startsWith('Edited'))) {
            if (line === 'New') {
                review.isNew = true;
                review.dateString = 'New';
                review.date = new Date();
            } else if (line.startsWith('Edited')) {
                review.dateString = line;
                review.date = parseRelativeDate(line.replace('Edited ', ''));
            } else {
                review.dateString = line;
                review.date = parseRelativeDate(line);
            }
            foundDate = true;
        }
        // Reactions
        else if (/^[❤️🙏]\d+/.test(line)) {
            review.reactions = line;
        }
        // Skip photo references and standalone numbers
        else if (!line.includes('Photo') && !line.match(/^\d+$/) && line !== 'New') {
            // This is likely review text
            textStarted = true;
            if (review.text) {
                review.text += ' ' + line;
            } else {
                review.text = line;
            }
        }
        
        i++;
    }
    
    review.nextIndex = i;
    return review;
}

function main() {
    try {
        const inputFile = 'raw-reviews/New Bank Health Centre-reviews.txt';
        const outputFile = 'parsed-reviews.json';
        
        if (!fs.existsSync(inputFile)) {
            console.error(`Input file not found: ${inputFile}`);
            return;
        }
        
        const textContent = fs.readFileSync(inputFile, 'utf-8');
        const reviews = parseReviews(textContent);
        
        const result = {
            businessName: 'New Bank Health Centre',
            address: '339 Stockport Rd, Longsight, Manchester M12 4JE, United Kingdom',
            averageRating: 2.0,
            totalReviews: 146,
            parsedReviews: reviews.length,
            reviews: reviews
        };
        
        fs.writeFileSync(outputFile, JSON.stringify(result, null, 2));
        
        console.log(`\n✅ Successfully parsed ${reviews.length} reviews`);
        console.log(`📁 Output saved to: ${outputFile}`);
        
        // Show some stats
        const withDates = reviews.filter(r => r.date).length;
        const withReactions = reviews.filter(r => r.reactions).length;
        const newReviews = reviews.filter(r => r.isNew).length;
        
        console.log(`Reviews with dates: ${withDates}`);
        console.log(`Reviews with reactions: ${withReactions}`);
        console.log(`New reviews: ${newReviews}`);
        
    } catch (error) {
        console.error('Error parsing reviews:', error.message);
    }
}

if (require.main === module) {
    main();
}

module.exports = { parseReviews, parseRelativeDate }; 