import React from "react";

const SuggestionBar = ({ images }) => {
  return (
    <div className="suggestion-bar">
      {images.map((image, index) => (
        <div key={index} className="suggestion-image-container">
          <img src={image.src} alt={image.alt} className="suggestion-image" />
          <p className="suggestion-image-text">{image.text}</p>
        </div>
      ))}
    </div>
  );
};

export default SuggestionBar;