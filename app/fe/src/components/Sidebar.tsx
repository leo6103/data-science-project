import React from 'react';
import { useMode } from '../context/ModeContext';
import clsx from 'clsx';
import logo from '../assets/logo.png'; // Đảm bảo đường dẫn đúng đến logo
import StatisticForm from './StatisticForm';
import PredictForm from './PredictForm';

const Sidebar: React.FC = () => {
  const { mode, toggleMode } = useMode();

  return (
    <div className="flex flex-col h-full">
      <div className="flex items-center justify-between bg-gray-200 p-4 shadow-md">
        <img src={logo} alt="React Logo" className="h-8" />
        <div>
          <button
            className={clsx(
              'p-2 rounded transition-colors duration-300 border mx-2',
              mode === 'predict' ? 'bg-primary text-white' : 'bg-base text-dark border-gray-300'
            )}
            onClick={() => toggleMode('predict')}
          >
            Predict
          </button>
          <button
            className={clsx(
              'p-2 rounded transition-colors duration-300 border',
              mode === 'statistic' ? 'bg-primary text-white' : 'bg-base text-dark border-gray-300'
            )}
            onClick={() => toggleMode('statistic')}
          >
            Statistic
          </button>
        </div>
      </div>
      <div className="flex-1 p-4">
        {/* Content based on mode, you can insert a form or other components here */}
        {mode === 'predict' ? (
          <PredictForm/>
        ) : (
          <StatisticForm/>
        )}
      </div>
    </div>
  );
};

export default Sidebar;
