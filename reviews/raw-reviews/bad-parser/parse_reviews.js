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
        
        // Check if this is likely a reviewer name or owner response
        if (isLikelyReviewerName(line, reviewLines, i) || line === 'New Bank Health Centre (owner)') {
            const review = parseReviewBlock(reviewLines, i);
            if (review && (review.text.trim() || review.isOwner)) {
                reviews.push(review);
            }
            i = review ? review.nextIndex : i + 1;
        } else {
            i++;
        }
    }
    
    // Sort by date (newest first), but keep owner responses near their related reviews
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
    if (line === 'New Bank Health Centre (owner)') return false; // Handle separately
    
    // Be much more liberal - look for context patterns
    const nextLine = allLines[currentIndex + 1];
    const lineAfterNext = allLines[currentIndex + 2];
    const lineAfterThat = allLines[currentIndex + 3];
    
    // If next line is Local Guide info, this is definitely a reviewer name
    if (nextLine && nextLine.includes('Local Guide·')) return true;
    
    // If followed by review count pattern
    if (nextLine && /^\d+\s+reviews?(\s*·.*)?$/i.test(nextLine)) return true;
    
    // If followed by date pattern
    if (nextLine && (nextLine.includes('ago') || nextLine === 'New' || nextLine.startsWith('Edited'))) return true;
    
    // If second line after is a date
    if (lineAfterNext && (lineAfterNext.includes('ago') || lineAfterNext === 'New' || lineAfterNext.startsWith('Edited'))) return true;
    
    // If third line after is a date (sometimes there's review count, then local guide, then date)
    if (lineAfterThat && (lineAfterThat.includes('ago') || lineAfterThat === 'New' || lineAfterThat.startsWith('Edited'))) return true;
    
    // Look for name patterns - be very inclusive
    if (isPersonNamePattern(line)) {
        return true;
    }
    
    // If it's not obviously metadata and looks like it could be a name or username
    if (!line.includes('Photo') && 
        !line.startsWith('Rating:') && 
        !/^[❤️🙏]+\d*$/.test(line) &&
        !line.match(/^\d+$/) &&
        line.length > 1 && line.length < 100) {
        
        // Look ahead to see if this could start a review block
        let hasReviewContent = false;
        for (let j = currentIndex + 1; j < Math.min(currentIndex + 6, allLines.length); j++) {
            const lookAhead = allLines[j];
            if (lookAhead && lookAhead.length > 20 && !lookAhead.includes('Photo')) {
                hasReviewContent = true;
                break;
            }
        }
        
        if (hasReviewContent) return true;
    }
    
    return false;
}

function isPersonNamePattern(text) {
    // Be very liberal with name detection
    if (!text || text.length < 2 || text.length > 100) return false;
    if (text.includes('…More')) return false;
    if (text.startsWith('Rating:')) return false;
    if (text.includes('Photo')) return false;
    if (/^[❤️🙏]+\d*$/.test(text)) return false;
    if (text.match(/^\d+$/)) return false;
    
    // Skip obvious metadata
    if (/^\d+\s+reviews?(\s*·.*)?$/i.test(text)) return false;
    if (text.includes('Local Guide·')) return false;
    if (text.includes('ago') && text.split(' ').length < 3) return false;
    if (text === 'New') return false;
    if (text.startsWith('Edited')) return false;
    
    // If it has reasonable name characteristics
    if (/^[A-Z]/.test(text)) return true; // Starts with capital
    if (text.includes(' ') && text.split(' ').length <= 5) return true; // Has spaces but not too many words
    if (/^[a-zA-Z0-9_\- ]+$/.test(text) && text.length > 2) return true; // Alphanumeric with reasonable chars
    
    return false;
}

function parseReviewBlock(lines, startIndex) {
    const isOwner = lines[startIndex] === 'New Bank Health Centre (owner)';
    
    const review = {
        reviewer: lines[startIndex],
        localGuideInfo: '',
        date: null,
        dateString: '',
        text: '',
        reactions: '',
        isNew: false,
        isOwner: isOwner,
        nextIndex: startIndex + 1
    };
    
    let i = startIndex + 1;
    let foundDate = false;
    
    while (i < lines.length) {
        const line = lines[i];
        
        if (!line) {
            i++;
            continue;
        }
        
        // Stop if we hit another reviewer or owner response (but be more permissive)
        if ((isLikelyReviewerName(line, lines, i) || line === 'New Bank Health Centre (owner)') && i > startIndex + 1) {
            break;
        }
        
        // Local Guide info
        if (line.includes('Local Guide·') && !review.localGuideInfo) {
            review.localGuideInfo = line;
        }
        // Review count info (like "1 review", "6 reviews")
        else if (/^\d+\s+reviews?(\s*·.*)?$/i.test(line) && !review.localGuideInfo) {
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
        // Reactions (emojis with numbers)
        else if (/^[❤️🙏]\d+/.test(line) || /^[❤️🙏]+\d+$/.test(line)) {
            if (review.reactions) {
                review.reactions += ' ' + line;
            } else {
                review.reactions = line;
            }
        }
        // Everything else goes into text - be very inclusive
        else if (line && line !== 'New') {
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

function cleanObject(obj) {
    const cleaned = {};
    for (const [key, value] of Object.entries(obj)) {
        if (value !== null && value !== undefined && value !== '' && value !== false) {
            if (Array.isArray(value)) {
                const cleanedArray = value.map(item => 
                    typeof item === 'object' ? cleanObject(item) : item
                ).filter(item => item !== null && item !== undefined && item !== '');
                if (cleanedArray.length > 0) {
                    cleaned[key] = cleanedArray;
                }
            } else if (typeof value === 'object') {
                const cleanedNested = cleanObject(value);
                if (Object.keys(cleanedNested).length > 0) {
                    cleaned[key] = cleanedNested;
                }
            } else {
                cleaned[key] = value;
            }
        }
    }
    return cleaned;
}

function generatePlaintext(reviews) {
    let plaintext = '';
    
    for (let i = 0; i < reviews.length; i++) {
        const review = reviews[i];
        plaintext += `\n${'='.repeat(80)}\n`;
        plaintext += `Review #${i + 1}\n`;
        plaintext += `${'='.repeat(80)}\n`;
        
        if (review.isOwner) {
            plaintext += `🏢 OWNER RESPONSE\n`;
        } else {
            plaintext += `👤 Reviewer: ${review.reviewer}\n`;
        }
        
        if (review.localGuideInfo) {
            plaintext += `📋 ${review.localGuideInfo}\n`;
        }
        
        if (review.dateString) {
            plaintext += `📅 Date: ${review.dateString}\n`;
        }
        
        if (review.isNew) {
            plaintext += `🆕 NEW REVIEW\n`;
        }
        
        if (review.text) {
            plaintext += `\n💬 Review:\n${review.text}\n`;
        }
        
        if (review.reactions) {
            plaintext += `\n👍 Reactions: ${review.reactions}\n`;
        }
        
        plaintext += '\n';
    }
    
    return plaintext;
}

function main() {
    try {
        const inputFile = 'raw-reviews/New Bank Health Centre-reviews.txt';
        const jsonOutputFile = 'parsed-reviews.json';
        const txtOutputFile = 'parsed-reviews.txt';
        
        if (!fs.existsSync(inputFile)) {
            console.error(`Input file not found: ${inputFile}`);
            return;
        }
        
        const textContent = fs.readFileSync(inputFile, 'utf-8');
        const reviews = parseReviews(textContent);
        
        // Clean reviews to remove falsy properties
        const cleanedReviews = reviews.map(review => cleanObject(review));
        
        const result = cleanObject({
            businessName: 'New Bank Health Centre',
            address: '339 Stockport Rd, Longsight, Manchester M12 4JE, United Kingdom',
            averageRating: 2.0,
            totalReviews: 146,
            parsedReviews: cleanedReviews.length,
            reviews: cleanedReviews
        });
        
        // Write JSON output
        fs.writeFileSync(jsonOutputFile, JSON.stringify(result, null, 2));
        
        // Write plaintext output
        const plaintextContent = `NEW BANK HEALTH CENTRE - GOOGLE REVIEWS
${'='.repeat(80)}
📍 Address: ${result.address}
⭐ Average Rating: ${result.averageRating}/5
📊 Total Reviews: ${result.totalReviews}
📈 Parsed Reviews: ${result.parsedReviews}
${'='.repeat(80)}

${generatePlaintext(cleanedReviews)}`;
        
        fs.writeFileSync(txtOutputFile, plaintextContent);
        
        console.log(`\n✅ Successfully parsed ${cleanedReviews.length} reviews`);
        console.log(`📁 JSON output: ${jsonOutputFile}`);
        console.log(`📄 Text output: ${txtOutputFile}`);
        
        // Show some stats
        const withDates = cleanedReviews.filter(r => r.date).length;
        const withReactions = cleanedReviews.filter(r => r.reactions).length;
        const newReviews = cleanedReviews.filter(r => r.isNew).length;
        const ownerResponses = cleanedReviews.filter(r => r.isOwner).length;
        
        console.log(`📅 Reviews with dates: ${withDates}`);
        console.log(`👍 Reviews with reactions: ${withReactions}`);
        console.log(`🆕 New reviews: ${newReviews}`);
        console.log(`🏢 Owner responses: ${ownerResponses}`);
        
    } catch (error) {
        console.error('Error parsing reviews:', error.message);
    }
}

if (require.main === module) {
    main();
}

module.exports = { parseReviews, parseRelativeDate }; 