/**
 * Dashboard Screen - Real-Time System Monitoring
 */

import React, {useEffect, useState} from 'react';
import {View, StyleSheet, ScrollView, RefreshControl} from 'react-native';
import {Card, Title, Paragraph, ProgressBar, useTheme, Chip} from 'react-native-paper';
import Icon from 'react-native-vector-icons/MaterialCommunityIcons';
import {WebSocketService, SystemMetrics} from '../services/WebSocketService';

const DashboardScreen = () => {
  const theme = useTheme();
  const [metrics, setMetrics] = useState<SystemMetrics | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    // Subscribe to metrics updates
    const onMetrics = (data: SystemMetrics) => {
      setMetrics(data);
    };

    const onConnected = () => {
      setIsConnected(true);
    };

    const onDisconnected = () => {
      setIsConnected(false);
    };

    WebSocketService.on('metrics', onMetrics);
    WebSocketService.on('connected', onConnected);
    WebSocketService.on('disconnected', onDisconnected);

    // Check current connection status
    setIsConnected(WebSocketService.isConnected());

    return () => {
      WebSocketService.off('metrics', onMetrics);
      WebSocketService.off('connected', onConnected);
      WebSocketService.off('disconnected', onDisconnected);
    };
  }, []);

  const onRefresh = React.useCallback(() => {
    setRefreshing(true);
    WebSocketService.requestMetrics();
    setTimeout(() => setRefreshing(false), 1000);
  }, []);

  const getStatusColor = (value: number, thresholds: {warn: number; critical: number}) => {
    if (value >= thresholds.critical) return theme.colors.error;
    if (value >= thresholds.warn) return '#ff9800';
    return theme.colors.primary;
  };

  return (
    <ScrollView
      style={styles.container}
      refreshControl={
        <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
      }>
      {/* Connection Status */}
      <View style={styles.statusBar}>
        <Chip
          icon={() => (
            <Icon
              name={isConnected ? 'check-circle' : 'close-circle'}
              size={16}
              color={isConnected ? '#4caf50' : theme.colors.error}
            />
          )}
          style={[
            styles.statusChip,
            {
              backgroundColor: isConnected
                ? 'rgba(76, 175, 80, 0.2)'
                : 'rgba(244, 67, 54, 0.2)',
            },
          ]}>
          {isConnected ? 'Connected' : 'Disconnected'}
        </Chip>
      </View>

      {/* FPS Counter */}
      {metrics?.fps !== null && (
        <Card style={styles.card}>
          <Card.Content>
            <View style={styles.metricHeader}>
              <Icon name="speedometer" size={24} color={theme.colors.primary} />
              <Title style={styles.metricTitle}>FPS</Title>
            </View>
            <View style={styles.fpsContainer}>
              <Paragraph style={styles.fpsValue}>
                {metrics?.fps?.toFixed(0) || '--'}
              </Paragraph>
              <Paragraph style={styles.fpsLabel}>Frames/Second</Paragraph>
            </View>
          </Card.Content>
        </Card>
      )}

      {/* CPU Card */}
      <Card style={styles.card}>
        <Card.Content>
          <View style={styles.metricHeader}>
            <Icon name="cpu-64-bit" size={24} color={theme.colors.primary} />
            <Title style={styles.metricTitle}>CPU</Title>
          </View>

          <View style={styles.metricRow}>
            <Paragraph>Usage</Paragraph>
            <Paragraph style={styles.metricValue}>
              {metrics?.cpu_usage?.toFixed(1) || '--'}%
            </Paragraph>
          </View>
          <ProgressBar
            progress={(metrics?.cpu_usage || 0) / 100}
            color={getStatusColor(metrics?.cpu_usage || 0, {
              warn: 70,
              critical: 90,
            })}
            style={styles.progressBar}
          />

          <View style={styles.metricRow}>
            <Paragraph>Temperature</Paragraph>
            <Paragraph style={styles.metricValue}>
              {metrics?.cpu_temp?.toFixed(0) || '--'}°C
            </Paragraph>
          </View>
          <ProgressBar
            progress={(metrics?.cpu_temp || 0) / 100}
            color={getStatusColor(metrics?.cpu_temp || 0, {
              warn: 75,
              critical: 85,
            })}
            style={styles.progressBar}
          />
        </Card.Content>
      </Card>

      {/* GPU Card */}
      <Card style={styles.card}>
        <Card.Content>
          <View style={styles.metricHeader}>
            <Icon name="expansion-card" size={24} color={theme.colors.primary} />
            <Title style={styles.metricTitle}>GPU</Title>
          </View>

          <View style={styles.metricRow}>
            <Paragraph>Usage</Paragraph>
            <Paragraph style={styles.metricValue}>
              {metrics?.gpu_usage?.toFixed(1) || '--'}%
            </Paragraph>
          </View>
          <ProgressBar
            progress={(metrics?.gpu_usage || 0) / 100}
            color={getStatusColor(metrics?.gpu_usage || 0, {
              warn: 85,
              critical: 95,
            })}
            style={styles.progressBar}
          />

          <View style={styles.metricRow}>
            <Paragraph>Temperature</Paragraph>
            <Paragraph style={styles.metricValue}>
              {metrics?.gpu_temp?.toFixed(0) || '--'}°C
            </Paragraph>
          </View>
          <ProgressBar
            progress={(metrics?.gpu_temp || 0) / 100}
            color={getStatusColor(metrics?.gpu_temp || 0, {
              warn: 75,
              critical: 85,
            })}
            style={styles.progressBar}
          />
        </Card.Content>
      </Card>

      {/* RAM Card */}
      <Card style={styles.card}>
        <Card.Content>
          <View style={styles.metricHeader}>
            <Icon name="memory" size={24} color={theme.colors.primary} />
            <Title style={styles.metricTitle}>RAM</Title>
          </View>

          <View style={styles.metricRow}>
            <Paragraph>Usage</Paragraph>
            <Paragraph style={styles.metricValue}>
              {metrics?.ram_usage?.toFixed(1) || '--'}%
            </Paragraph>
          </View>
          <ProgressBar
            progress={(metrics?.ram_usage || 0) / 100}
            color={getStatusColor(metrics?.ram_usage || 0, {
              warn: 80,
              critical: 95,
            })}
            style={styles.progressBar}
          />
        </Card.Content>
      </Card>

      {/* Power Card */}
      <Card style={styles.card}>
        <Card.Content>
          <View style={styles.metricHeader}>
            <Icon name="flash" size={24} color={theme.colors.primary} />
            <Title style={styles.metricTitle}>Power</Title>
          </View>

          <View style={styles.metricRow}>
            <Paragraph>Consumption</Paragraph>
            <Paragraph style={styles.metricValue}>
              {metrics?.power_watts?.toFixed(0) || '--'}W
            </Paragraph>
          </View>
          <ProgressBar
            progress={Math.min((metrics?.power_watts || 0) / 500, 1)}
            color={getStatusColor(metrics?.power_watts || 0, {
              warn: 350,
              critical: 450,
            })}
            style={styles.progressBar}
          />
        </Card.Content>
      </Card>

      <View style={styles.footer}>
        <Paragraph style={styles.timestamp}>
          Last Update: {metrics?.timestamp ? new Date(metrics.timestamp).toLocaleTimeString() : '--'}
        </Paragraph>
      </View>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 16,
  },
  statusBar: {
    marginBottom: 16,
    alignItems: 'center',
  },
  statusChip: {
    marginVertical: 8,
  },
  card: {
    marginBottom: 16,
    elevation: 4,
  },
  metricHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 16,
  },
  metricTitle: {
    marginLeft: 8,
    fontSize: 18,
  },
  metricRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginTop: 8,
  },
  metricValue: {
    fontWeight: 'bold',
    fontSize: 16,
  },
  progressBar: {
    height: 8,
    borderRadius: 4,
    marginTop: 4,
    marginBottom: 8,
  },
  fpsContainer: {
    alignItems: 'center',
    paddingVertical: 16,
  },
  fpsValue: {
    fontSize: 48,
    fontWeight: 'bold',
  },
  fpsLabel: {
    fontSize: 14,
    opacity: 0.7,
  },
  footer: {
    alignItems: 'center',
    marginVertical: 16,
  },
  timestamp: {
    opacity: 0.6,
    fontSize: 12,
  },
});

export default DashboardScreen;
