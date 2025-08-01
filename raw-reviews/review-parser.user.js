function parseGoogleMapsReviews() {
  // Select all review containers, including owner replies
  const reviewElements = document.querySelectorAll('div.bwb7ce, div.bwb7ce [class*="owner"]');
  
  // Array to store parsed reviews
  const reviews = [];
  
  reviewElements.forEach(element => {
    try {
      // Extract reviewer's name
      const nameElement = element.querySelector('.Vpc5Fe');
      const reviewerName = nameElement ? nameElement.textContent.trim() : 'Unknown';
      
      // Extract rating
      const ratingElements = element.querySelectorAll('.dHX2k svg.ePMStd');
      const rating = ratingElements.length > 0 
        ? Array.from(ratingElements).filter(svg => svg.querySelector('path').getAttribute('fill') !== '#dadce0').length
        : 0;
      
      // Extract review text
      const reviewTextElement = element.querySelector('.OA1nbd');
      const reviewText = reviewTextElement ? reviewTextElement.textContent.trim() : '';
      
      // Extract number of reactions
      const reactionElement = element.querySelector('.uo5PT');
      const reactions = reactionElement 
        ? parseInt(reactionElement.textContent.replace(/[^\d]/g, '')) || 0
        : 0;
      
      // Extract date (e.g., "2 months ago")
      const dateElement = element.querySelector('.svzjne > div > span:not(.XVR0jd), .svzjne > span:not(.XVR0jd)');
      const reviewDate = dateElement ? dateElement.textContent.trim() : 'Unknown';
      
      // Determine if it's an owner reply
      const isOwnerReply = element.querySelector('[class*="owner"]') !== null || reviewerName.includes('New Bank Health Centre');
      
      // Create review object
      const review = {
        reviewerName,
        rating,
        reviewText,
        reactions,
        reviewDate,
        isOwnerReply
      };
      
      reviews.push(review);
    } catch (error) {
      console.error('Error parsing review:', error);
    }
  });
  
  // Log the results
  console.log('Parsed Reviews:', reviews);
  
  // Return the reviews array
  return reviews;
}

// Execute the parser
parseGoogleMapsReviews();