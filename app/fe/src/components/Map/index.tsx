import React from 'react';
import { GoogleMap, LoadScript, Marker } from '@react-google-maps/api';

interface MapComponentProps {
  markerPosition: { lat: number; lng: number } | null;
  setMarkerPosition: (position: { lat: number; lng: number }) => void;
}

const MapComponent: React.FC<MapComponentProps> = ({ markerPosition, setMarkerPosition }) => {
  const mapStyles = {
    height: "400px",
    width: "100%"
  };

  const defaultCenter = {
    lat: 21.0285,  // Tọa độ của Hà Nội
    lng: 105.8542  // Tọa độ của Hà Nội
  };

  const handleMapClick = (event: google.maps.MapMouseEvent) => {
    if (event.latLng) {
      const lat = event.latLng.lat();
      const lng = event.latLng.lng();
      setMarkerPosition({ lat, lng });
    }
  };

  return (
    <div
      className="relative flex items-center justify-center w-full h-full bg-cover bg-center"
      style={{
        backgroundImage: `url("/hanoibackground.jpg")`,
      }}
    >
      <div className="w-full h-full bg-white bg-opacity-80 rounded-lg">
        <LoadScript googleMapsApiKey={import.meta.env.VITE_MAP_API_KEY || ''}>
          <GoogleMap
            mapContainerStyle={mapStyles}
            zoom={13}
            center={markerPosition || defaultCenter}
            onClick={handleMapClick}
            options={{
              draggableCursor: "crosshair"
            }}
          >
            {markerPosition && <Marker position={markerPosition} />}
          </GoogleMap>
        </LoadScript>
      </div>
    </div>
  );
};

export default MapComponent;
