import React, { useState } from 'react';
import './TimeMachine.scss';

interface TimeMachineProps {
  onTimeChange: (date: Date) => void;
}

export const TimeMachine: React.FC<TimeMachineProps> = ({ onTimeChange }) => {
  const [currentDate, setCurrentDate] = useState(new Date());
  const [isPlaying, setIsPlaying] = useState(false);
  
  const handleDateChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newDate = new Date(e.target.value);
    setCurrentDate(newDate);
    onTimeChange(newDate);
  };
  
  const handlePlayPause = () => {
    setIsPlaying(!isPlaying);
    // TODO: Implement time animation
  };
  
  return (
    <div className="time-machine">
      <div className="time-machine-title">Time Machine</div>
      <div className="time-controls">
        <input
          type="date"
          value={currentDate.toISOString().split('T')[0]}
          onChange={handleDateChange}
          className="date-input"
        />
        <button 
          className={`play-button ${isPlaying ? 'playing' : ''}`}
          onClick={handlePlayPause}
        >
          {isPlaying ? '⏸' : '▶'}
        </button>
      </div>
    </div>
  );
};