import React, { useRef, useEffect, useState } from "react";
import "./Visual.css";
import io from "socket.io-client";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import {
  faEraser,
  faUndo,
  faRedo,
  faSave,
  faCircle,
  faSquare,
  faPlay,
  faPencil,
  faPaperPlane,
  faCircleNodes,
  faSquarePen,
} from "@fortawesome/free-solid-svg-icons";
import SuggestionBar from "./SuggestionBar";
import { height } from "@fortawesome/free-solid-svg-icons/fa0";

const Board = ({ username }) => {
  // console.log("re-rendered")
  const canvasRef = useRef(null);
  const socketRef = useRef();
  const [isDrawing, setIsDrawing] = useState(false);
  const [isAutoDrawing, setIsAutoDrawing] = useState(false);
  
  const [lastRectStartX, setlastRectStartX] = useState(-1);
  const [lastRectStartY, setlastRectStartY] = useState(-1);
  const [lastRectWidth, setlastRectWidth] = useState(-1);
  const [lastRectLength, setlastRectLength] = useState(-1);
  const [currSelectionRect, setcurrSelectionRect] = useState(null);
  /////
  const [drawingStartpoint, setDrawingStartpoint] = useState(null);
  const [XMax, setXMax] = useState(0);
  const [XMin, setXMin] = useState(0);
  const [YMax, setYMax] = useState(0);
  const [YMin, setYMin] = useState(0);
  /////
  const imgPos = {
    x: -1,
    y: -1,
    width: 0,
    height: 0,
  }
  const ImagePosRef = useRef(imgPos); 
  //const [isDragging, setisDragging] = useState(false);
  const DraggingRef = useRef(false);
  const imgMovingRef = useRef(false);

  /////
  const [prevPosition, setPrevPosition] = useState({ x: 0, y: 0 });
  const [brushColor, setBrushColor] = useState("black");
  const [brushSize, setBrushSize] = useState(2);
  const [isErasing, setIsErasing] = useState(false);
  const [canvasHistory, setCanvasHistory] = useState([]);
  const [canvasHistoryIndex, setCanvasHistoryIndex] = useState(-1);
  const [selectedShape, setSelectedShape] = useState(null);
  const [messageText, setMessageText] = useState(""); 
   const [suggestionImages, setSuggestionImages] = useState([
    { src: "/images/suggestion1.png", alt: "Suggestion Image 1", text: "Image 1" },
    { src: "/images/suggestion2.png", alt: "Suggestion Image 2", text: "Image 2" },
    // Add more images as needed
  ]);
  const [images, setImages] = useState([]);

  // Added state for drawing data points
  const [drawingData, setDrawingData] = useState([]);
  const [lastDataPoint, setLastDataPoint] = useState(null);
  useEffect(() => {
    handleResize();

    window.addEventListener("resize", handleResize);

    socketRef.current = io("http://localhost:3001");
    socketRef.current.on("draw", (data) => {
      const canvas = canvasRef.current;
      const context = canvas.getContext("2d");
      context.lineCap = "round";
      if (data.isDrawing) {
        // Draw freehand drawing point
        drawFreehandPoint(context, data);
      } else if (data.isErasing) {
        // Erase
        drawReceivedShape(context, data);
      } else {
        // Draw shape
        drawReceivedShape(context, data);
      }
    });
    socketRef.current.on("undo", handleUndoFromServer);
    socketRef.current.on("redo", handleRedoFromServer);
    socketRef.current.on("clearCanvas", handleClearCanvas);
    socketRef.current.on("newMessage", handleMessageReceive);

    return () => {
      window.removeEventListener("resize", handleResize);
      socketRef.current.off("draw");
      socketRef.current.off("undo");
      socketRef.current.off("redo");
      socketRef.current.off("clearCanvas");
      socketRef.current.off("newMessage");

    };
  }, []);

  // useEffect(() => {
  //     const fetchData = async () => {
  //         try {
  //             const response = await fetch('http://127.0.0.1:8000/getimage');
  //             if (!response.ok) {
  //                 throw new Error('Network response was not ok');
  //             }
  //             const data = await response.json();
  //             if (data.success > 0) {
  //                 // Limit to fetch only 4 images
  //                 const fetchedImages = data.images.slice(0, 4).map(imageData => {
  //                     const byteCharacters = atob(imageData.image);
  //                     const byteNumbers = new Array(byteCharacters.length);
  //                     for (let i = 0; i < byteCharacters.length; i++) {
  //                         byteNumbers[i] = byteCharacters.charCodeAt(i);
  //                     }
  //                     const byteArray = new Uint8Array(byteNumbers);
  //                     const imageUrl = URL.createObjectURL(new Blob([byteArray], { type: 'image/png' }));
  //                     return imageUrl;
  //                 });
  //                 setImages(fetchedImages);
  //             } else {
  //                 console.log("No images found");
  //             }
  //         } catch (error) {
  //             console.error('There was a problem with the fetch operation:', error);
  //         }
  //     };

  //     fetchData();
  // }, []);

  const handleMessageReceive = (data) => {
    const messagesList = document.querySelector(".messages-list");
    const newMessageUsername = document.createElement("p");
    newMessageUsername.textContent = data.username;
    newMessageUsername.className = "message-sender";
    messagesList.appendChild(newMessageUsername);
    const newMessageTime = document.createElement("p");
    newMessageTime.textContent = data.messageTime;
    newMessageTime.className = "message-time";
    messagesList.appendChild(newMessageTime);
    const newMessage = document.createElement("p");
    newMessage.textContent = data.messageContent;
    newMessage.className = "message-text";
    messagesList.appendChild(newMessage);
  }

  const handleUndoFromServer = (data) => {
    if (canvasHistoryIndex > 0) {
      setCanvasHistoryIndex(canvasHistoryIndex - 1);
      const canvas = canvasRef.current;
      const context = canvas.getContext("2d");
      const img = new Image();
      img.src = canvasHistory[canvasHistoryIndex - 1];
      img.onload = () => {
        context.clearRect(0, 0, canvas.width, canvas.height);
        context.drawImage(img, 0, 0);
      };
    }
    setSelectedShape(null); // Deselect the current shape
  };

  const handleRedoFromServer = (data) => {
    if (canvasHistoryIndex < canvasHistory.length - 1) {
      setCanvasHistoryIndex(canvasHistoryIndex + 1);
      const canvas = canvasRef.current;
      const context = canvas.getContext("2d");
      const img = new Image();
      img.src = canvasHistory[canvasHistoryIndex + 1];
      img.onload = () => {
        context.clearRect(0, 0, canvas.width, canvas.height);
        context.drawImage(img, 0, 0);
      };
    }
    setSelectedShape(null); // Deselect the current shape
  };

  const handleClearCanvas = () => {
    const canvas = canvasRef.current;
    const context = canvas.getContext("2d");
    context.clearRect(0, 0, canvas.width, canvas.height);
    setCanvasHistory([]);
    setCanvasHistoryIndex(-1);
    setSelectedShape(null); // Deselect the current shape
  };

  const drawFreehandPoint = (context, data) => {
    const { x, y, color, size, isErasing } = data;
    context.strokeStyle = isErasing ? "white" : color;
    context.lineWidth = isErasing ? size * 6 : size; // Adjust size for eraser
  
    context.beginPath();
    context.moveTo(x - 1, y); // Move to the previous position to draw a continuous line
    context.lineTo(x, y);
    context.stroke();
  };





  const drawReceivedShape = (context, data) => {
    const { shape, x, y, radius, width, height, color, size } = data;
    context.strokeStyle = color;
    // context.lineWidth = size;

    switch (shape) {
      case "circle":
        context.beginPath();
        context.arc(x, y, radius* (size / 10), 0, 2 * Math.PI);
        context.stroke();
        break;
      case "square":
      case "rectangle":
        context.beginPath();
        context.rect(x - width / 2, y - height / 2, width, height);
        context.stroke();
        break;
      case "triangle":
        const halfWidth = width / 2;
        const halfHeight = (Math.sqrt(3) * halfWidth) / 2;
        context.beginPath();
        context.moveTo(x, y - halfHeight);
        context.lineTo(x + halfWidth, y + halfHeight);
        context.lineTo(x - halfWidth, y + halfHeight);
        context.closePath();
        context.stroke();
        break;
      default:
        // Handle unsupported shapes
        console.error("Unsupported shape:", shape);
    }
  };

  const handleMouseDown = (e) => {
    if (selectedShape) {
      // Draw shape
      drawShape(e);
      return;
    }
    
    setIsDrawing(true);
    const startPosition = {
      x: e.nativeEvent.offsetX,
      y: e.nativeEvent.offsetY,
    };
    setPrevPosition(startPosition);
    /// new logic
    if(drawingStartpoint == null)
    {
      setDrawingStartpoint(startPosition);
      setXMax(startPosition.x);
      setXMin(startPosition.x);
      setYMax(startPosition.y);
      setYMin(startPosition.y);
    }
    /// new logic
    // Capture starting point for drawing
    const dataPoint = {
      x: startPosition.x,
      y: startPosition.y,
      color: brushColor,
      size: brushSize,
      isErasing: isErasing? true : false,
      isDrawing: true, // Indicate that drawing has started
    };
    setDrawingData([dataPoint]); // Start with this point

    // Emit starting point to the server
    socketRef.current.emit("draw", dataPoint);
  };

  const handleMouseUp = () => {
    ////
    console.log("XMax:", XMax);
    console.log("XMin:", XMin);
    console.log("YMax:", YMax);
    console.log("YMin:", YMin);
    ////

    setIsDrawing(false);
    if (canvasHistoryIndex !== canvasHistory.length - 1) {
      // If we draw after undo, clear the future history
      setCanvasHistory(canvasHistory.slice(0, canvasHistoryIndex + 1));
    }
    const canvas = canvasRef.current;
    setCanvasHistory([...canvasHistory, canvas.toDataURL()]);
    setCanvasHistoryIndex(canvasHistory.length);
    
    if(isAutoDrawing){
      if(lastRectWidth == -1){
        ///
        const width = XMax+30 - XMin;
        const height = YMax+30 - YMin;
        const rectStartX=XMin-20;
        const rectStartY=YMin-20;
        // Draw the rectangle using the saved coordinates
        
        const context = canvas.getContext("2d");
        
        context.lineWidth = 0.5;
        context.strokeStyle = "grey";
        context.strokeRect( rectStartX, rectStartY, width, height);

        const RectPoint = {
          StartX: rectStartX,
          StartY: rectStartY,
          width: width,
          height: height,
        };
        setcurrSelectionRect(RectPoint);

        setlastRectStartX(rectStartX);
        setlastRectStartY(rectStartY);
        setlastRectWidth(width);
        setlastRectLength(height);
        ///
      }
      else{
        ///
        const width = XMax+30 - XMin;
        const height = YMax+30 - YMin;
        const rectStartX=XMin-20;
        const rectStartY=YMin-20;
        // Draw the rectangle using the saved coordinates
        const context = canvas.getContext("2d");
        // Remove the last rectangle
        context.lineWidth = 1;
        context.strokeStyle = "white";
        context.strokeRect( lastRectStartX, lastRectStartY, lastRectWidth, lastRectLength);

        context.strokeStyle = "grey";
        context.strokeRect( rectStartX, rectStartY, width, height);
        const RectPoint = {
          StartX: rectStartX,
          StartY: rectStartY,
          width: width,
          height: height,
        };
        setcurrSelectionRect(RectPoint);
        setlastRectStartX(rectStartX);
        setlastRectStartY(rectStartY);
        setlastRectWidth(width);
        setlastRectLength(height);
        ///

      }
    }
  };

  const handleMouseMove = (e) => {
    if (!isDrawing) return;

    if (selectedShape) return; // Don't draw freehand when a shape is selected

    if (DraggingRef.current) return;  // Don't draw freehand when an image is being dragged

    const canvas = canvasRef.current;
    const context = canvas.getContext("2d");

    const newPosition = { x: e.nativeEvent.offsetX, y: e.nativeEvent.offsetY };

    context.beginPath();
    context.moveTo(prevPosition.x, prevPosition.y);
    context.lineTo(newPosition.x, newPosition.y);

    if (isErasing) {
      context.strokeStyle = "white"; // Set eraser color
      context.lineWidth = brushSize * 6; // Adjust eraser size
    } else {
      context.strokeStyle = brushColor;
      context.lineWidth = brushSize;
    }

    context.stroke();

    setPrevPosition(newPosition);

    // Capture data point for drawing
    const dataPoint = {
      x: newPosition.x,
      y: newPosition.y,
      color: brushColor,
      size: brushSize,
      isErasing,
      isDrawing: true, // Indicate that drawing is ongoing
    };
    setDrawingData((prevData) => [...prevData, dataPoint]); // Add this point
    setLastDataPoint(dataPoint);

    // Update XMax, XMin, YMax, YMin
    setXMax((prev) => Math.max(prev, dataPoint.x));
    setXMin((prev) => Math.min(prev, dataPoint.x));
    setYMax((prev) => Math.max(prev, dataPoint.y));
    setYMin((prev) => Math.min(prev, dataPoint.y));
    // Emit data point to the server
    socketRef.current.emit("draw", dataPoint);
  };

  const drawShape = (e) => {
    const canvas = canvasRef.current;
    const context = canvas.getContext("2d");
    context.strokeStyle = brushColor;
    context.lineWidth = brushSize;

    const currentPosition = {
      x: e.nativeEvent.offsetX,
      y: e.nativeEvent.offsetY,
    };

    const fixedSize = 20; // Set the fixed size for all shapes

    let drawingData = {};

    if (selectedShape === "circle") {
      const radius = fixedSize / 2;
      context.beginPath();
      context.arc(currentPosition.x, currentPosition.y, radius, 0, 2 * Math.PI);

      drawingData = {
        shape: "circle",
        x: currentPosition.x,
        y: currentPosition.y,
        radius,
        color: brushColor,
        size: brushSize,
      };
    } else if (selectedShape === "square") {
      context.beginPath();
      context.rect(
        currentPosition.x - fixedSize / 2,
        currentPosition.y - fixedSize / 2,
        fixedSize,
        fixedSize
      );

      drawingData = {
        shape: "square",
        x: currentPosition.x,
        y: currentPosition.y,
        width: fixedSize,
        height: fixedSize,
        color: brushColor,
        size: brushSize,
      };
    } else if (selectedShape === "triangle") {
      context.beginPath();
      context.moveTo(currentPosition.x, currentPosition.y - fixedSize / 2);
      context.lineTo(
        currentPosition.x + (Math.sqrt(3) / 2) * (fixedSize / 2),
        currentPosition.y + fixedSize / 2
      );
      context.lineTo(
        currentPosition.x - (Math.sqrt(3) / 2) * (fixedSize / 2),
        currentPosition.y + fixedSize / 2
      );
      context.closePath();

      drawingData = {
        shape: "triangle",
        x: currentPosition.x,
        y: currentPosition.y,
        width: fixedSize,
        height: (Math.sqrt(3) / 2) * (fixedSize / 2),
        color: brushColor,
        size: brushSize,
      };
    } else if (selectedShape === "rectangle") {
      context.beginPath();
      context.rect(
        currentPosition.x - fixedSize / 2,
        currentPosition.y - fixedSize / 2 / 2,
        fixedSize,
        fixedSize / 2
      );

      drawingData = {
        shape: "rectangle",
        x: currentPosition.x,
        y: currentPosition.y,
        width: fixedSize,
        height: fixedSize / 2,
        color: brushColor,
        size: brushSize,
      };
    }
    // Add handling for other shapes similarly

    context.stroke();

    // Emit drawing data to the server
    socketRef.current.emit("draw", drawingData);
  };

  const handleBrushColorChange = (color) => {
    setIsErasing(false);

    setBrushColor(color);
  };

  const handleBrushSizeChange = (size) => {
    setIsErasing(false);
    setSelectedShape(null); // Deselect the current shape
    setBrushSize(size);
  };

  const handleEraser = () => {
    setSelectedShape(null); // Deselect the current shape
    setIsErasing(true);
  };

  const handleClear = () => {
    const canvas = canvasRef.current;
    const context = canvas.getContext("2d");
    context.clearRect(0, 0, canvas.width, canvas.height);
    setCanvasHistory([]);
    setCanvasHistoryIndex(-1);
    setSelectedShape(null); // Deselect the current shape
    setDrawingStartpoint(null);
    const imgPos = {
      x: -1,
      y: -1,
      width: 0,
      height: 0,
    }
    ImagePosRef.current= imgPos; 
    console.log(ImagePosRef.current)
    socketRef.current.emit("clearCanvas", drawingData);
  };

  const handleUndo = () => {
    if (canvasHistoryIndex > 0) {
      setCanvasHistoryIndex(canvasHistoryIndex - 1);
      const canvas = canvasRef.current;
      const context = canvas.getContext("2d");
      const img = new Image();
      img.src = canvasHistory[canvasHistoryIndex - 1];
      img.onload = () => {
        context.clearRect(0, 0, canvas.width, canvas.height);
        context.drawImage(img, 0, 0);
      };
    }
    setSelectedShape(null); // Deselect the current shape
    socketRef.current.emit("undo", drawingData);
  };

  const handleImageClick = (canvas, imageUrl) => {
      
      setIsErasing(false);
      setSelectedShape(null);
      setIsAutoDrawing(false);
      setIsDrawing(false);
      const context = canvas.getContext('2d');
      context.strokeStyle = "white";
      context.clearRect(currSelectionRect.StartX-1, currSelectionRect.StartY-1, currSelectionRect.width+2, currSelectionRect.height+2);

      // Clear the canvas

      // Create a new Image object for the clicked image
      const image = new Image();
      image.onload = () => {
          
          let offsetX = 0;
          let offsetY = 0;
          let imageX = currSelectionRect.StartX; // Initial x-coordinate of the image
          let imageY = currSelectionRect.StartY; // Initial y-coordinate of the image
          // Draw the image at its initial position
          drawImage(imageX, imageY);

          // Function to draw the image at a specific position
          function drawImage(currX, currY) {
              const prevX = ImagePosRef.current.x;
              const prevY = ImagePosRef.current.y;
              if(prevX != -1){
                context.clearRect(prevX, prevY, currSelectionRect.width, currSelectionRect.height);
                context.drawImage(image, currX, currY, currSelectionRect.width, currSelectionRect.height); // Adjust size as needed
                ImagePosRef.current = {
                  x: currX,
                  y: currY,
                  width: currSelectionRect.width,
                  height: currSelectionRect.height,
                }
            }
            else{
              context.drawImage(image, currX, currY, currSelectionRect.width, currSelectionRect.height); // Adjust size as needed
                ImagePosRef.current = {
                  x: currX,
                  y: currY,
                  width: currSelectionRect.width,
                  height: currSelectionRect.height,
                }
              console.log(ImagePosRef.current);
            }
          }
  
          // Add event listener for dragging the image
          canvas.addEventListener('mousedown', (event) => {    
            // x: e.nativeEvent.offsetX,
            // y: e.nativeEvent.offsetY,
            const rect = canvas.getBoundingClientRect();
            offsetX = event.clientX - rect.left;
            offsetY = event.clientY - rect.top;
            const x = event.clientX - rect.left;
            const y = event.clientY - rect.top;

            // Check if the click is within the image area
            if (x >= imageX && x <= imageX + currSelectionRect.width && y >= imageY && y <= imageY + currSelectionRect.height) {
                DraggingRef.current= true;
            }
          });
  
          canvas.addEventListener('mousemove', (event) => {
              if (DraggingRef.current) {
                  const rect = canvas.getBoundingClientRect();
                  const x = event.clientX - rect.left;
                  const y = event.clientY - rect.top;
                  imageX = x;
                  imageY = y;

                  if(imgMovingRef.current == false)
                  {
                  context.clearRect(currSelectionRect.StartX, currSelectionRect.StartY, ImagePosRef.current.width, ImagePosRef.current.height);
                  imgMovingRef.current = true;
                  }
              }
          });
  
          canvas.addEventListener('mouseup', (event) => {
            DraggingRef.current= false;
            const rect = canvas.getBoundingClientRect();
                  const x = event.clientX - rect.left;
                  const y = event.clientY - rect.top;
                  imageX = x;
                  imageY = y;
            if(imgMovingRef.current == true){
              drawImage(imageX, imageY);
              imgMovingRef.current = false;
            }
          });
      };
      image.src = imageUrl;
  };

  const handleRedo = () => {
    if (canvasHistoryIndex < canvasHistory.length - 1) {
      setCanvasHistoryIndex(canvasHistoryIndex + 1);
      const canvas = canvasRef.current;
      const context = canvas.getContext("2d");
      const img = new Image();
      img.src = canvasHistory[canvasHistoryIndex + 1];
      img.onload = () => {
        context.clearRect(0, 0, canvas.width, canvas.height);
        context.drawImage(img, 0, 0);
      };
    }
    setSelectedShape(null); // Deselect the current shape
    socketRef.current.emit("redo", drawingData);
  };

  const handleSave = () => {
    const canvas = canvasRef.current;
    const link = document.createElement("a");
    link.download = "drawing.png";
    link.href = canvas.toDataURL();
    link.click();
  };

  const fetchData = async () => {
      try {
          const response = await fetch('http://127.0.0.1:8000/getimage');
          if (!response.ok) {
              throw new Error('Network response was not ok');
          }
          const data = await response.json();
          if (data.success > 0) {
              // Limit to fetch only 4 images
              const fetchedImages = data.images.slice(0, 4).map(imageData => {
                  const byteCharacters = atob(imageData.image);
                  const byteNumbers = new Array(byteCharacters.length);
                  for (let i = 0; i < byteCharacters.length; i++) {
                      byteNumbers[i] = byteCharacters.charCodeAt(i);
                  }
                  const byteArray = new Uint8Array(byteNumbers);
                  const imageUrl = URL.createObjectURL(new Blob([byteArray], { type: 'image/png' }));
                  return imageUrl;
              });
              setImages(fetchedImages);
          } else {
              console.log("No images found");
          }
      } catch (error) {
          console.error('There was a problem with the fetch operation:', error);
      }
  };


  const handleSendCanvas = async () => {
      setDrawingStartpoint(null);
      const canvas = canvasRef.current;
      const context = canvas.getContext("2d");

      const x = currSelectionRect.StartX;
      const y = currSelectionRect.StartY;
      const RectWidth = currSelectionRect.width;
      const RectHeight = currSelectionRect.height;
      console.log(x,y,RectWidth);

      //const imageData = context.getImageData(x, y, RectWidth, RectHeight);
      
      //making a new canvas to put the imageData
      const newCanvas = document.createElement('canvas');
      const newCanvasContext = newCanvas.getContext("2d");
      newCanvas.width = RectWidth;
      newCanvas.height = RectHeight;
      
      // Draw the specified region from the original canvas onto the new canvas
      newCanvasContext.drawImage(canvas, x, y, RectWidth, RectHeight, 0, 0, RectWidth, RectWidth);
      //

      const image = newCanvas.toDataURL("image/png"); // Returns a data URL string
      console.log(image);
      const response = await fetch("http://127.0.0.1:8000/predict", {
          method: "POST",
          headers: {
              "Content-Type": "application/json",
          },
          body: JSON.stringify({ image }), // Send the data URL directly
      });

      if (!response.ok) {
          console.error("Error sending canvas image");
      } else {
          console.log("Canvas image sent successfully");
          fetchData();
      }

      setMessageText(""); // Clear the message input after sending
  };

  const handleShapeSelect = (shape) => {
    setIsErasing(false);
    setSelectedShape(shape);
  };

  const handleFreeStyleDrawing = () => {
    setIsErasing(false);
    setSelectedShape(null);
    setIsAutoDrawing(false);
    setDrawingStartpoint(null);
    const imgPos = {
      x: -1,
      y: -1,
      width: 0,
      height: 0,
    }
    ImagePosRef.current= imgPos; 
  };

  const handleAutoDrawing = () => {
    setIsErasing(false);
    setSelectedShape(null);
    setIsAutoDrawing(true);
    setDrawingStartpoint(null);
    const imgPos = {
      x: -1,
      y: -1,
      width: 0,
      height: 0,
    }
    ImagePosRef.current= imgPos; 
  };

  const handleResize = () => {
    const canvas = canvasRef.current;
    if (canvas) {
      const context = canvas.getContext("2d");
      const imageData = context.getImageData(0, 0, canvas.width, canvas.height);

      // Set canvas width to a percentage of the window's inner width
      canvas.width = window.innerWidth * 0.75;

      // Maintain the aspect ratio while resizing the canvas
      canvas.height = canvas.width * (canvas.height / canvas.width);

      context.putImageData(imageData, 0, 0);
    }
  };
  
  const handleMessageSend = () => {
    if(messageText) {
      let messageData = {
        messageContent: messageText,
        username: username,
        messageTime: new Date()
      }
      socketRef.current.emit("newMessage", messageData);
      setMessageText("");
    }
  }

  return (
    <>
      <div className="">
        <div className="row">
          <div className="col-10">
            <div className="row align-items-center">
              <div className="col-6">
                <h3 className="mb-0 text-start ms-5 fw-bolder">Visual Teach</h3>
                <p className="text-start ms-5">Hi, {username}</p>
              </div>
              <div className="col-6 d-flex justify-content-left">
                <img src="/images/logo-transparent.png" alt="" />
              </div>
            </div>
            <div className="d-flex my-3 ms-5 align-items-center">
              <label htmlFor="brush-size" className="fw-bold ms-4">Size </label>
              <input
                type="range"
                className="ms-2"
                id="brush-size"
                min="1"
                max="10"
                value={brushSize}
                onChange={(e) => handleBrushSizeChange(e.target.value)}
              />
            </div>
            <div className="canvas-container">
              <div className="menu-bar rounded ms-2">
                <div className="brush-controls">
                  <button
                    className={`btn text-black fs-5 mb-1 d-block ${brushColor === 'black' ? 'active' : ''}`}
                    onClick={() => handleBrushColorChange("black")}
                  >
                    <FontAwesomeIcon icon={faSquare} />
                  </button>
                  <button
                    className={`btn text-danger fs-5 mb-1 d-block ${brushColor === 'red' ? 'active' : ''}`}
                    onClick={() => handleBrushColorChange("red")}
                  >
                    <FontAwesomeIcon icon={faSquare} />
                  </button>
                  <button
                    className={`btn text-primary fs-5 mb-1 d-block ${brushColor === 'blue' ? 'active' : ''}`}
                    onClick={() => handleBrushColorChange("blue")}
                  >
                    <FontAwesomeIcon icon={faSquare} />
                  </button>
                </div>
                <div className="brush-controls">
                  <div
                    className="btn text-white fs-5 mb-1 d-block"
                    onClick={handleFreeStyleDrawing}
                  >
                    <FontAwesomeIcon icon={faPencil} />
                  </div>
                  <div
                    className="btn text-white fs-5 mb-1 d-block"
                    onClick={handleAutoDrawing}
                  >
                    <FontAwesomeIcon icon={faSquarePen} />
                  </div>
                  <div
                    className="btn text-white fs-5 mb-1 d-block"
                    onClick={handleEraser}
                  >
                    <FontAwesomeIcon icon={faEraser} />
                  </div>
                  <div
                    className="btn text-white fs-6 mb-1 d-block"
                    onClick={handleClear}
                  >
                    Clear
                  </div>
                  <div
                    className="btn text-white fs-5 mb-1 d-block"
                    onClick={handleUndo}
                    disabled={canvasHistoryIndex <= 0}
                  >
                    <FontAwesomeIcon icon={faUndo} />
                  </div>
                  <div
                    className="btn text-white fs-5 mb-1 d-block"
                    onClick={handleRedo}
                    disabled={canvasHistoryIndex === canvasHistory.length - 1}
                  >
                    <FontAwesomeIcon icon={faRedo} />
                  </div>
                  <div
                    className="btn text-white fs-5 mb-1 d-block"
                    onClick={handleSave}
                  >
                    <FontAwesomeIcon icon={faSave} />
                  </div>
                </div>
                <div className="brush-controls">
                  <div
                    className={`btn text-white fs-5 mb-1 d-block ${selectedShape==="circle" ? "active": ""}`}
                    onClick={() => handleShapeSelect("circle")}
                  >
                    <FontAwesomeIcon icon={faCircle} />
                  </div>
                  <div
                    className={`btn text-white fs-5 mb-1 d-block ${selectedShape==="square" ? "active": ""}`}
                    onClick={() => handleShapeSelect("square")}
                  >
                    <FontAwesomeIcon icon={faSquare} />
                  </div>
                  <div
                    className={`btn text-white fs-5 mb-1 d-block ${selectedShape==="triangle" ? "active": ""}`}
                    onClick={() => handleShapeSelect("triangle")}
                  >
                    <FontAwesomeIcon
                      icon={faPlay}
                      style={{ transform: "rotate(30deg)" }}
                    />
                  </div>
                  <div
                    className={`btn text-white fs-5 mb-1 d-block ${selectedShape==="rectangle" ? "active": ""}`}
                    onClick={() => handleShapeSelect("rectangle")}
                  >
                    <FontAwesomeIcon
                      icon={faSquare}
                      style={{ transform: "scaleX(1.5)" }}
                    />
                  </div>
                  <div className="btn text-white fs-5 mb-1 d-block" onClick={handleSendCanvas}>
                    <FontAwesomeIcon icon={faCircleNodes} />
                  </div>
                </div>
              </div>

              <div>
                <canvas
                  ref={canvasRef}
                  className="board bg-white"
                  width={1150} // Set your desired width
                  height={550} // Set your desired height
                  onMouseDown={handleMouseDown}
                  onMouseUp={handleMouseUp}
                  onMouseMove={handleMouseMove}
                />
                <div id="image-container" className="flex-wrap justify-content-around align-items-center mt-3" style={{ backgroundColor: 'lightblue' }}>
                    {images.map((imageUrl, index) => (
                        <img
                            key={index}
                            src={imageUrl}
                            className="img-thumbnail"
                            style={{ width: '150px', height: '150px', marginLeft: '25px', marginRight: '25px' }}
                            onClick={() => handleImageClick(canvasRef.current, imageUrl)}
                        />
                    ))}
                </div>
              </div>
            </div>
          </div>
          <div
            className="col-2 px-0 text-white comment-section comment-body position-sticky top-0 end-0"
          >
            <div className="d-flex flex-column h-100">
              <div className="py-2 comment-heading">
                <h5 className="mt-3">Comments</h5>
              </div>
              <div
                className="overflow-auto pt-3 text-start px-3 fs-6"
                style={{ flex: 1 }}
              >
                <div className="mx-0 messages-list">
                  
                </div>
              </div>
              <div
                className="py-3 px-1 position-relative comment-heading"
              >
                <div className="input-group">
                  <input
                    type="text"
                    className="form-control"
                    name="message"
                    placeholder="Enter comment"
                    value={messageText}
                    onChange={ (e) => setMessageText(e.target.value)}
                    style={{
                      backgroundColor: "#345BA0",
                      color: "lightgray",
                      border: "none",
                    }}
                  />
                  <button
                    className="btn bg-success position-absolute end-0 rounded-2"
                    onClick={handleMessageSend}
                    style={{ zIndex: 30 }}
                  >
                    <FontAwesomeIcon icon={faPaperPlane} />
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </>
  );
};

export default Board;
