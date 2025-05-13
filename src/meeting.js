import React, { useEffect, useRef, useState } from "react";

const Meeting = () => {
  const [messages, setMessages] = useState([]);
  const [isMicOn, setIsMicOn] = useState(true);
  const [isCamOn, setIsCamOn] = useState(true);
  const localStream = useRef(null);
  const localVideoRef = useRef(null);

  useEffect(() => {
    const startLocalStream = async () => {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({
          video: true,
          audio: true,
        });
        localStream.current = stream;

        if (localVideoRef.current) {
          localVideoRef.current.srcObject = stream;
        }
      } catch (err) {
        console.error("Không thể truy cập camera/mic:", err);
      }
    };

    startLocalStream();
  }, []);

  const toggleMic = () => {
    if (localStream.current) {
      localStream.current.getAudioTracks().forEach((track) => {
        track.enabled = !isMicOn;
      });
      setIsMicOn(!isMicOn);
    }
  };

  const toggleCam = () => {
    if (localStream.current) {
      localStream.current.getVideoTracks().forEach((track) => {
        track.enabled = !isCamOn;
      });
      setIsCamOn(!isCamOn);
    }
  };

  const sendMessage = (msg) => {
    setMessages((prev) => [...prev, msg]);
  };

  return (
    <div style={{ display: "flex", height: "100vh", backgroundColor: "#121212", color: "#fff" }}>
      {/* Video */}
      <div style={{ flex: 3, position: "relative" }}>
        <video
          ref={localVideoRef}
          autoPlay
          muted
          style={{ width: "100%", height: "100%", objectFit: "cover" }}
        />
        {/* Controls */}
        <div style={{
          position: "absolute",
          bottom: "20px",
          left: "50%",
          transform: "translateX(-50%)",
          display: "flex",
          gap: "10px"
        }}>
          <button onClick={toggleMic} style={btnStyle}>
            {isMicOn ? "Tắt Mic" : "Bật Mic"}
          </button>
          <button onClick={toggleCam} style={btnStyle}>
            {isCamOn ? "Tắt Camera" : "Bật Camera"}
          </button>
        </div>
      </div>

      {/* Chat */}
      <div style={{
        flex: 1,
        backgroundColor: "#1f1f1f",
        display: "flex",
        flexDirection: "column",
        padding: "1rem"
      }}>
        <div style={{ flex: 1, overflowY: "auto", marginBottom: "1rem" }}>
          {messages.map((msg, index) => (
            <div key={index} style={{ marginBottom: "5px" }}>{msg}</div>
          ))}
        </div>
        <input
          type="text"
          placeholder="Nhập tin nhắn..."
          onKeyDown={(e) => {
            if (e.key === "Enter") {
              sendMessage(e.target.value);
              e.target.value = "";
            }
          }}
          style={{
            padding: "10px",
            borderRadius: "20px",
            border: "none",
            backgroundColor: "#333",
            color: "#fff"
          }}
        />
      </div>
    </div>
  );
};

const btnStyle = {
  backgroundColor: "#3c4043",
  color: "white",
  border: "none",
  padding: "10px 15px",
  borderRadius: "20px",
  cursor: "pointer",
};

export default Meeting;
