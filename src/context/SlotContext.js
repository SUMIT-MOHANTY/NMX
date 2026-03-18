import React, { createContext, useContext, useState } from 'react';

const SlotContext = createContext();

export const useSlotContext = () => useContext(SlotContext);

export const SlotContextProvider = ({ children }) => {
  const [selectedLocation, setSelectedLocation] = useState(null);
  const [selectedDate, setSelectedDate] = useState(new Date());

  const value = {
    selectedLocation,
    setSelectedLocation,
    selectedDate,
    setSelectedDate
  };

  return (
    <SlotContext.Provider value={value}>
      {children}
    </SlotContext.Provider>
  );
};
