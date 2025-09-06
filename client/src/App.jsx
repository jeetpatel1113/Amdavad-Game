// client/src/App.jsx
import { useEffect, useState } from "react";
import { socket } from "./socket";

export default function App() {
  const [state, setState] = useState({ message: "loading..." });
  const [local, setLocal] = useState("");

  useEffect(() => {
    socket.on("state", (s) => setState(s));
    socket.on("connect_error", (err) => console.error("Socket error", err));
    return () => {
      socket.off("state");
      socket.off("connect_error");
    };
  }, []);

  const send = () => {
    const newState = { message: local || "empty" };
    socket.emit("update", newState);
    setLocal("");
  };

  return (
    <div style={{ padding: 20 }}>
      <h1>Shared message: {state.message}</h1>
      <input
        value={local}
        onChange={(e) => setLocal(e.target.value)}
        placeholder="Type message"
      />
      <button onClick={send}>Update for everyone</button>
    </div>
  );
}
