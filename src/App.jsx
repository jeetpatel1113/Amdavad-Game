import { useState, useEffect } from "react";
import "./App.css";

export default function App() {
  const [diceStates, setDiceStates] = useState(Array(4).fill("white"));
  const [tokens, setTokens] = useState([]);
  const [availableTokens, setAvailableTokens] = useState({
    red: 4,
    blue: 4,
    green: 4,
    yellow: 4,
  });
  const [whiteCount, setWhiteCount] = useState(4);
  const [rollHistory, setRollHistory] = useState([]);
  const [moveCount, setMoveCount] = useState(0);

  const handleDiceClick = () => {
    const newDiceStates = Array(4)
      .fill(null)
      .map(() => (Math.random() < 0.5 ? "white" : "black"));

    const newWhiteCount = newDiceStates.filter(
      (color) => color === "white"
    ).length;
    setDiceStates(newDiceStates);
    setWhiteCount(newWhiteCount);
    setMoveCount((prev) => prev + 1);

    // Update roll history, keeping max of 5 entries
    setRollHistory((prev) => {
      const updatedHistory = [
        ...prev,
        { rollNumber: moveCount + 1, count: newWhiteCount },
      ];
      return updatedHistory.length > 5
        ? updatedHistory.slice(1)
        : updatedHistory;
    });
  };

  const renderBoard = () => {
    return Array(5)
      .fill(null)
      .map((_, row) => (
        <div key={row} className="row">
          {Array(5)
            .fill(null)
            .map((_, col) => {
              const isMiddleBox =
                ((row === 0 || row === 4) && col === 2) ||
                ((col === 0 || col === 4) && row === 2);
              const isCenterBox = row === 2 && col === 2;
              const className = `cell ${
                isMiddleBox || isCenterBox ? "marked-box" : ""
              }`;
              return <div key={col} className={className}></div>;
            })}
        </div>
      ));
  };

  const renderTokens = (color) => {
    return Array(availableTokens[color])
      .fill(null)
      .map((_, i) => (
        <div
          key={`${color}-${i}`}
          className="token"
          style={{ backgroundColor: color }}
          draggable="true"
          onDragStart={(e) => {
            const rect = e.target.getBoundingClientRect();
            e.dataTransfer.setData(
              "text/plain",
              JSON.stringify({
                id: `${color}-${i}`,
                color,
                offsetX: e.clientX - rect.left,
                offsetY: e.clientY - rect.top,
                isNew: true,
              })
            );
          }}
        />
      ));
  };

  useEffect(() => {
    const handleDragOver = (e) => e.preventDefault();
    const handleDrop = (e) => {
      e.preventDefault();
      try {
        const data = JSON.parse(e.dataTransfer.getData("text/plain"));
        if (data.isNew) {
          setAvailableTokens((prev) => ({
            ...prev,
            [data.color]: prev[data.color] - 1,
          }));
        }
        const newToken = {
          id: Date.now().toString(),
          color: data.color,
          x: e.clientX - data.offsetX,
          y: e.clientY - data.offsetY,
        };
        setTokens((prev) =>
          data.isNew
            ? [...prev, newToken]
            : [...prev.filter((t) => t.id !== data.id), newToken]
        );
      } catch (error) {
        console.error("Error processing drop:", error);
      }
    };

    document.addEventListener("dragover", handleDragOver);
    document.addEventListener("drop", handleDrop);

    return () => {
      document.removeEventListener("dragover", handleDragOver);
      document.removeEventListener("drop", handleDrop);
    };
  }, []);

  return (
    <main>
      {tokens.map((token) => (
        <div
          key={token.id}
          className="token dropped-token"
          style={{
            backgroundColor: token.color,
            left: `${token.x}px`,
            top: `${token.y}px`,
          }}
          draggable="true"
          onDragStart={(e) => {
            const rect = e.target.getBoundingClientRect();
            const tokenData = {
              id: token.id,
              color: token.color,
              offsetX: e.clientX - rect.left,
              offsetY: e.clientY - rect.top,
              isExisting: true,
            };
            e.dataTransfer.setData("text/plain", JSON.stringify(tokenData));
          }}
        />
      ))}
      <div className="game-container">
        <h1 className="game-title">Amdavad</h1>
        <div className="board">{renderBoard()}</div>
        <div className="text-bar">
          <h3>White Dice Count: {whiteCount}</h3>
          <h3>Move Count: {moveCount}</h3>
          <h4>Last 5 Rolls:</h4>
          <ul>
            {rollHistory.map((entry, index) => (
              <li key={index}>
                Roll {entry.rollNumber}: {entry.count} white
              </li>
            ))}
          </ul>
        </div>
        <div className="tokens-container">
          <div className="token-group">{renderTokens("red")}</div>
          <div className="token-group">{renderTokens("blue")}</div>
          <div className="token-group">{renderTokens("green")}</div>
          <div className="token-group">{renderTokens("yellow")}</div>
        </div>
        <div className="dice-container">
          {diceStates.map((state, i) => (
            <div
              key={i}
              className="dice"
              style={{ backgroundColor: state }}
              onClick={() => handleDiceClick(i)}
            />
          ))}
        </div>
      </div>
    </main>
  );
}
