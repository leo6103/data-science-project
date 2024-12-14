import React from 'react';
import { ModeProvider } from './context/ModeContext';
import MapComponent from './components/MapComponent';
import Sidebar from './components/Sidebar';

const App: React.FC = () => {
  return (
    <ModeProvider>
      <div className="flex h-screen">
        <div className="w-1/3 bg-gray-100"> {/* Thanh bar chiếm 30% màn hình */}
          <Sidebar />
        </div>
        <div className="w-2/3"> {/* Phần còn lại dành cho bản đồ */}
          <MapComponent />
        </div>
      </div>
    </ModeProvider>
  );
}

export default App;
