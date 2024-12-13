import React from "react";
import { GoogleMap, LoadScript, Marker } from "@react-google-maps/api";
import { useMode } from "../context/ModeContext";

const containerStyle = {
  width: "100%",
  height: "100%",
};

const defaultCenter = {
  lat: 20.990812301635742,
  lng: 105.7839126586914,
};

const MapComponent: React.FC = () => {
  const { mode, statistics, marker, setMarker } = useMode();
  const apiKey = import.meta.env.VITE_MAP_API_KEY;

  const handleMapClick = (event: google.maps.MapMouseEvent) => {
    if (mode === "predict" && event.latLng) {
      setMarker({
        lat: event.latLng.lat(),
        lng: event.latLng.lng(),
      });
    }
  };

  return (
    <LoadScript googleMapsApiKey={apiKey}>
      <GoogleMap
        mapContainerStyle={containerStyle}
        center={marker || defaultCenter}
        zoom={10}
        options={{
          draggableCursor: mode === "predict" ? "crosshair" : "grab",
        }}
        onClick={handleMapClick}
      >
        {mode === "predict" && marker && <Marker position={marker} />}

        {mode === "statistic" &&
          statistics.map((item, index) => (
            <Marker
              key={index}
              position={{ lat: item.latitude, lng: item.longitude }}
              icon={{
                path: google.maps.SymbolPath.CIRCLE,
                scale: 10,
                fillColor: item.color,
                fillOpacity: 1,
                strokeWeight: 0,
              }}
            />
          ))}
      </GoogleMap>
    </LoadScript>
  );
};

export default MapComponent;
