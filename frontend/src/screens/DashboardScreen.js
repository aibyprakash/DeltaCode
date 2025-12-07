import React, { useEffect, useState } from 'react';
import { View, Text, ScrollView, RefreshControl, StyleSheet } from 'react-native';
import client from '../api/client';

const DashboardCard = ({ label, value }) => (
  <View style={styles.card}>
    <Text style={styles.cardLabel}>{label}</Text>
    <Text style={styles.cardValue}>{value}</Text>
  </View>
);

const DashboardScreen = () => {
  const [metrics, setMetrics] = useState(null);
  const [refreshing, setRefreshing] = useState(false);

  const loadMetrics = async () => {
    setRefreshing(true);
    const response = await client.get('dashboard/owner-summary/');
    setMetrics(response.data);
    setRefreshing(false);
  };

  useEffect(() => {
    loadMetrics();
  }, []);

  if (!metrics) return <Text>Loading...</Text>;

  return (
    <ScrollView refreshControl={<RefreshControl refreshing={refreshing} onRefresh={loadMetrics} />}> 
      <Text style={styles.header}>Owner Dashboard</Text>
      <View style={styles.grid}>
        <DashboardCard label="Occupancy" value={`${metrics.occupancy_percent}%`} />
        <DashboardCard label="Guests" value={metrics.total_guests} />
        <DashboardCard label="Due Amount" value={`₹${metrics.total_due_amount}`} />
        <DashboardCard label="Open Complaints" value={metrics.active_complaints} />
      </View>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  header: { fontSize: 22, fontWeight: 'bold', margin: 16 },
  grid: { flexDirection: 'row', flexWrap: 'wrap', justifyContent: 'space-around' },
  card: { width: '45%', padding: 16, backgroundColor: '#f7f7f7', borderRadius: 8, marginBottom: 12 },
  cardLabel: { fontSize: 14, color: '#555' },
  cardValue: { fontSize: 20, fontWeight: 'bold', marginTop: 8 },
});

export default DashboardScreen;
