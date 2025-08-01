const fs = require('fs');
const cheerio = require('cheerio');

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
    
    return now;
}

function extractRating($ratingDiv) {
    const filledStars = $ratingDiv.find('svg path[fill="#fabb05"]').length;
    return filledStars;
}

function parseReviewsFromHTML(htmlContent) {
    const $ = cheerio.load(htmlContent);
    const reviews = [];
    
    // Find all review containers - using the pattern I saw in the HTML
    $('.bwb7ce').each((index, element) => {
        const $review = $(element);
        
        try {
            // Extract reviewer info
            const $reviewerLink = $review.find('.yC3ZMb').first();
            const reviewerName = $reviewerLink.find('.Vpc5Fe').text().trim();
            const reviewerInfo = $reviewerLink.find('.GSM50').text().trim();
            
            // Skip if no reviewer name found
            if (!reviewerName) return;
            
            // Check if this is an owner response - use proper CSS selectors
            const isOwner = $review.find('.PhaUTe').length > 0 || 
                           $review.find('[aria-label*="(owner)"]').length > 0 ||
                           reviewerName.includes('(owner)');
            
            // Extract rating
            const $ratingDiv = $review.find('.dHX2k').first();
            const rating = extractRating($ratingDiv);
            
            // Extract date
            const dateText = $review.find('.y3Ibjb').text().trim();
            let parsedDate = null;
            let isNew = false;
            
            if (dateText) {
                if (dateText === 'New') {
                    isNew = true;
                    parsedDate = new Date();
                } else if (dateText.includes('ago') || dateText.includes('Edited')) {
                    parsedDate = parseRelativeDate(dateText);
                } else {
                    // Try to parse other date formats
                    parsedDate = parseRelativeDate(dateText);
                }
            }
            
            // Also check for "New" indicator separately
            if ($review.find('.t5YfZe span').text().trim() === 'New') {
                isNew = true;
                if (!parsedDate) parsedDate = new Date();
            }
            
            // Extract review text - look for text content in the review
            let reviewText = '';
            
            // For owner responses, text is in .KmCjbd
            // For customer reviews, we need to look in different places
            if (isOwner) {
                const $ownerText = $review.find('.KmCjbd').first();
                if ($ownerText.length) {
                    reviewText = $ownerText.text().trim();
                }
            } else {
                // Look for other possible text containers
                const possibleSelectors = [
                    '.Dm8d4',  // Another potential text container
                    '[jscontroller="fIQYlf"]',  // Review content container
                    '.MyEned'   // Another review text class
                ];
                
                for (const selector of possibleSelectors) {
                    const $textElem = $review.find(selector).first();
                    if ($textElem.length && $textElem.text().trim().length > 20) {
                        reviewText = $textElem.text().trim();
                        break;
                    }
                }
                
                // Fallback: extract from the overall container but filter better
                if (!reviewText) {
                    const allText = $review.text();
                    const lines = allText.split('\n').map(line => line.trim()).filter(line => line);
                    
                    // Skip lines that look like metadata
                    const contentLines = lines.filter(line => 
                        !line.includes('Local Guide') &&
                        !line.includes('reviews') &&
                        !line.includes('photos') &&
                        !line.includes('ago') &&
                        !line.includes('Report review') &&
                        !line.includes('Review options') &&
                        line !== 'New' &&
                        line !== reviewerName &&
                        line !== reviewerInfo &&
                        line !== dateText &&
                        line.length > 15 &&
                        !line.match(/^[❤️🙏]+\d+$/) &&
                        !line.match(/^\d+$/)
                    );
                    
                    if (contentLines.length > 0) {
                        // Take meaningful content lines, but limit to avoid metadata
                        reviewText = contentLines.slice(0, 2).join(' ');
                    }
                }
            }
            
            // Extract reactions (emojis with numbers)
            let reactions = '';
            const reactionMatch = reviewText.match(/[❤️🙏]+\d+/g);
            if (reactionMatch) {
                reactions = reactionMatch.join(' ');
                // Remove reactions from review text
                reviewText = reviewText.replace(/[❤️🙏]+\d+/g, '').trim();
            }
            
            const review = {
                reviewer: reviewerName,
                reviewerInfo: reviewerInfo,
                isOwner: isOwner,
                rating: rating || null,
                date: parsedDate,
                dateString: dateText,
                isNew: isNew,
                text: reviewText,
                reactions: reactions
            };
            
            // Only add reviews with substantial content
            if (reviewText || isOwner) {
                reviews.push(review);
            }
            
        } catch (error) {
            console.warn(`Error parsing review ${index}:`, error.message);
        }
    });
    
    // Sort by date (newest first)
    reviews.sort((a, b) => {
        if (!a.date && !b.date) return 0;
        if (!a.date) return 1;
        if (!b.date) return -1;
        return new Date(b.date) - new Date(a.date);
    });
    
    return reviews;
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
        
        if (review.reviewerInfo) {
            plaintext += `📋 ${review.reviewerInfo}\n`;
        }
        
        if (review.rating) {
            plaintext += `⭐ Rating: ${review.rating}/5\n`;
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
        const inputFile = 'raw-reviews/New Bank Health Centre-reviews.html';
        const jsonOutputFile = 'parsed-reviews-html.json';
        const txtOutputFile = 'parsed-reviews-html.txt';
        
        if (!fs.existsSync(inputFile)) {
            console.error(`Input file not found: ${inputFile}`);
            return;
        }
        
        console.log('🔄 Reading HTML file...');
        const htmlContent = fs.readFileSync(inputFile, 'utf-8');
        
        console.log('🔍 Parsing HTML structure...');
        const reviews = parseReviewsFromHTML(htmlContent);
        
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
        const plaintextContent = `NEW BANK HEALTH CENTRE - GOOGLE REVIEWS (HTML PARSED)
${'='.repeat(80)}
📍 Address: ${result.address}
⭐ Average Rating: ${result.averageRating}/5
📊 Total Reviews: ${result.totalReviews}
📈 Parsed Reviews: ${result.parsedReviews}
${'='.repeat(80)}

${generatePlaintext(cleanedReviews)}`;
        
        fs.writeFileSync(txtOutputFile, plaintextContent);
        
        console.log(`\n✅ Successfully parsed ${cleanedReviews.length} reviews from HTML`);
        console.log(`📁 JSON output: ${jsonOutputFile}`);
        console.log(`📄 Text output: ${txtOutputFile}`);
        
        // Show some stats
        const withRatings = cleanedReviews.filter(r => r.rating).length;
        const withDates = cleanedReviews.filter(r => r.date).length;
        const withReactions = cleanedReviews.filter(r => r.reactions).length;
        const newReviews = cleanedReviews.filter(r => r.isNew).length;
        const ownerResponses = cleanedReviews.filter(r => r.isOwner).length;
        
        console.log(`⭐ Reviews with ratings: ${withRatings}`);
        console.log(`📅 Reviews with dates: ${withDates}`);
        console.log(`👍 Reviews with reactions: ${withReactions}`);
        console.log(`🆕 New reviews: ${newReviews}`);
        console.log(`🏢 Owner responses: ${ownerResponses}`);
        
    } catch (error) {
        console.error('❌ Error parsing HTML reviews:', error.message);
    }
}

if (require.main === module) {
    main();
}

module.exports = { parseReviewsFromHTML, parseRelativeDate };