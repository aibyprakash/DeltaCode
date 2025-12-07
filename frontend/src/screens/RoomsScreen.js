import React, { useEffect, useState } from 'react';
import { View, Text, FlatList, StyleSheet } from 'react-native';
import client from '../api/client';

const RoomCard = ({ room }) => (
  <View style={styles.card}>
    <Text style={styles.title}>{room.room_number} • {room.room_type}</Text>
    <Text>{`Rent/bed: ₹${room.rent_per_bed}`}</Text>
    <Text>{`Max beds: ${room.max_beds}`}</Text>
    <Text>Status: {room.is_active ? 'Active' : 'Inactive'}</Text>
  </View>
);

const RoomsScreen = () => {
  const [rooms, setRooms] = useState([]);

  useEffect(() => {
    client.get('rooms/').then((response) => setRooms(response.data.results || response.data));
  }, []);

  return (
    <FlatList
      data={rooms}
      keyExtractor={(item) => String(item.id)}
      renderItem={({ item }) => <RoomCard room={item} />}
      contentContainerStyle={styles.list}
      ListEmptyComponent={<Text style={styles.empty}>No rooms yet</Text>}
    />
  );
};

const styles = StyleSheet.create({
  list: { padding: 16 },
  card: { padding: 16, borderRadius: 8, backgroundColor: '#fff', marginBottom: 12, elevation: 1 },
  title: { fontSize: 16, fontWeight: 'bold' },
  empty: { textAlign: 'center', marginTop: 40, color: '#777' },
});

export default RoomsScreen;
