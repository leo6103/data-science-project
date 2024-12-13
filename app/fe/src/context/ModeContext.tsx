import React, { createContext, useContext, useState, ReactNode } from "react";

type ModeContextType = {
  mode: string;
  toggleMode: (newMode: string) => void;

  statistics: any[];
  setStatistics: (data: any[]) => void;
  
  marker: { lat: number; lng: number } | null;
  setMarker: (marker: { lat: number; lng: number } | null) => void;
};

const ModeContext = createContext<ModeContextType | undefined>(undefined);

export const useMode = () => {
  const context = useContext(ModeContext);
  if (!context) throw new Error("useMode must be used within a ModeProvider");
  return context;
};

interface ModeProviderProps {
  children: ReactNode;
}

export const ModeProvider: React.FC<ModeProviderProps> = ({ children }) => {
  const [mode, setMode] = useState<string>("predict");
  const [statistics, setStatistics] = useState<any[]>([]);
  const [marker, setMarker] = useState<{ lat: number; lng: number } | null>(null);

  const toggleMode = (newMode: string) => {
    setMode(newMode);
  };

  return (
    <ModeContext.Provider value={{ mode, toggleMode, statistics, setStatistics, marker, setMarker }}>
      {children}
    </ModeContext.Provider>
  );
};
