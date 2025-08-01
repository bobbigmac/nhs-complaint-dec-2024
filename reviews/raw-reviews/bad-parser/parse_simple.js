const fs = require('fs');

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
    
    return null;
}

function extractMainContent(textContent) {
    const lines = textContent.split('\n').map(line => line.replace(/^\s*\d+→/, '').trim()).filter(line => line);
    const reviews = [];
    
    let i = 0;
    while (i < lines.length) {
        const line = lines[i];
        
        // Skip header/metadata lines
        if (i < 20 || !line || line.length < 3) {
            i++;
            continue;
        }
        
        // Look for potential reviewer names or owner responses
        if (isLikelyReviewStart(line, lines, i)) {
            const review = extractSingleReview(lines, i);
            if (review.text || review.reviewer) {
                reviews.push(review);
            }
            i = review.nextIndex;
        } else {
            i++;
        }
    }
    
    return reviews;
}

function isLikelyReviewStart(line, lines, index) {
    // Owner responses
    if (line === 'New Bank Health Centre (owner)') return true;
    
    // Skip obvious non-reviewer lines
    if (line.includes('ago') && line.length < 15) return false;
    if (line.includes('Local Guide') && !line.includes('·')) return false;
    if (/^[❤️🙏]\d+$/.test(line)) return false;
    if (line === 'New' && lines[index + 1]?.includes('ago')) return false;
    if (/^\d+$/.test(line)) return false;
    if (line.includes('Photo') && line.includes('review by')) return false;
    
    // Skip metadata patterns that aren't names
    if (/^\d+\s+(review|photo)s?$/i.test(line)) return false; // "4 reviews", "2 photos"
    if (/^\d+\s+(review|photo)s?·\d+\s+(review|photo)s?$/i.test(line)) return false; // "4 reviews·2 photos"
    if (line.includes('reviews') && !line.includes(' ')) return false; // standalone "reviews"
    if (line.includes('photos') && !line.includes(' ')) return false; // standalone "photos"
    
    // Names are usually:
    // - Not too long (under 50 chars)
    // - Don't contain obvious review content indicators
    // - Either single names or "First Last" pattern
    if (line.length > 50) return false;
    if (line.includes('...More')) return false;
    if (line.includes('appointment') || line.includes('service') || line.includes('terrible')) return false;
    
    // Better name pattern: either contains letters and spaces (real names) or is a single word username
    // But exclude pure numbers and metadata
    if (/^[A-Za-z\s'-]+$/.test(line) && line.length > 2) return true; // Real names
    if (/^[A-Za-z][A-Za-z0-9_]+$/.test(line) && line.length > 3) return true; // Usernames
    
    return false;
}

function extractSingleReview(lines, startIndex) {
    const review = {
        reviewer: lines[startIndex],
        text: '',
        date: null,
        dateString: '',
        isOwner: false,
        isNew: false,
        reactions: '',
        nextIndex: startIndex + 1
    };
    
    // Check if this is an owner response
    if (lines[startIndex] === 'New Bank Health Centre (owner)') {
        review.isOwner = true;
    }
    
    let i = startIndex + 1;
    let textLines = [];
    let foundDate = false;
    
    while (i < lines.length) {
        const line = lines[i];
        
        if (!line) {
            i++;
            continue;
        }
        
        // Stop if we hit another review start
        if (isLikelyReviewStart(line, lines, i)) {
            break;
        }
        
        // Handle dates
        if (!foundDate && (line.includes('ago') || line === 'New' || line.includes('Edited'))) {
            review.dateString = line;
            if (line === 'New') {
                review.isNew = true;
                review.date = new Date();
            } else if (line.includes('ago') || line.includes('Edited')) {
                review.date = parseRelativeDate(line);
            }
            foundDate = true;
        }
        // Handle reactions
        else if (/^[❤️🙏]\d+$/.test(line) || /^[❤️🙏][❤️🙏]\d+$/.test(line)) {
            review.reactions = line;
        }
        // Skip Local Guide info and other metadata
        else if (line.includes('Local Guide') || 
                 line.includes('reviews') && line.includes('photos') ||
                 /^\d+\s+(review|photo)s?$/.test(line)) {
            // Skip metadata
        }
        // Everything else is potentially review text
        else if (line.length > 5 && 
                 !line.includes('Photo') && 
                 !line.includes('review by') &&
                 line !== review.reviewer) {
            textLines.push(line);
        }
        
        i++;
    }
    
    // Join text lines
    review.text = textLines.join(' ').trim();
    
    // Clean up text - remove excessive ellipsis, normalize spaces
    review.text = review.text.replace(/…More$/, '').replace(/\s+/g, ' ').trim();
    
    review.nextIndex = i;
    return review;
}

function outputResults(reviews, outputDir = '.') {
    const jsonOutput = {
        businessName: 'New Bank Health Centre',
        totalParsed: reviews.length,
        reviews: reviews.sort((a, b) => {
            if (a.date && b.date) return b.date - a.date;
            if (a.date) return -1;
            if (b.date) return 1;
            return 0;
        })
    };
    
    // Write JSON (clean, no falsy properties)
    const cleanReviews = reviews.map(review => {
        const clean = {};
        Object.keys(review).forEach(key => {
            if (review[key]) clean[key] = review[key];
        });
        return clean;
    });
    
    const jsonFile = `${outputDir}/parsed-reviews-simple.json`;
    fs.writeFileSync(jsonFile, JSON.stringify({
        ...jsonOutput,
        reviews: cleanReviews
    }, null, 2));
    
    // Write plaintext
    const txtFile = `${outputDir}/parsed-reviews-simple.txt`;
    let txtContent = `NEW BANK HEALTH CENTRE REVIEWS\n`;
    txtContent += `Total Reviews Parsed: ${reviews.length}\n`;
    txtContent += `Generated: ${new Date().toISOString()}\n\n`;
    txtContent += '='.repeat(80) + '\n\n';
    
    reviews.forEach((review, index) => {
        txtContent += `REVIEW #${index + 1}\n`;
        txtContent += `-`.repeat(40) + '\n';
        if (review.reviewer) txtContent += `Reviewer: ${review.reviewer}\n`;
        if (review.dateString) txtContent += `Date: ${review.dateString}\n`;
        if (review.isOwner) txtContent += `Type: Owner Response\n`;
        if (review.isNew) txtContent += `Status: New\n`;
        if (review.reactions) txtContent += `Reactions: ${review.reactions}\n`;
        txtContent += '\n';
        if (review.text) {
            txtContent += `${review.text}\n`;
        }
        txtContent += '\n' + '='.repeat(80) + '\n\n';
    });
    
    fs.writeFileSync(txtFile, txtContent);
    
    return { jsonFile, txtFile, count: reviews.length };
}

function main() {
    try {
        const inputFile = 'raw-reviews/New Bank Health Centre-reviews.txt';
        
        if (!fs.existsSync(inputFile)) {
            console.error(`Input file not found: ${inputFile}`);
            return;
        }
        
        console.log('📂 Reading text file...');
        const textContent = fs.readFileSync(inputFile, 'utf-8');
        
        console.log('🔍 Extracting main content...');
        const reviews = extractMainContent(textContent);
        
        console.log('💾 Writing output files...');
        const result = outputResults(reviews);
        
        console.log(`\n✅ Successfully parsed ${result.count} reviews`);
        console.log(`📄 JSON: ${result.jsonFile}`);
        console.log(`📝 Text: ${result.txtFile}`);
        
        // Show breakdown
        const ownerResponses = reviews.filter(r => r.isOwner).length;
        const customerReviews = reviews.length - ownerResponses;
        const withDates = reviews.filter(r => r.date).length;
        const withReactions = reviews.filter(r => r.reactions).length;
        
        console.log(`\n📊 Breakdown:`);
        console.log(`   Customer Reviews: ${customerReviews}`);
        console.log(`   Owner Responses: ${ownerResponses}`);
        console.log(`   With Dates: ${withDates}`);
        console.log(`   With Reactions: ${withReactions}`);
        
    } catch (error) {
        console.error('❌ Error:', error.message);
    }
}

if (require.main === module) {
    main();
}