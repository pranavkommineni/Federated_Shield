import { useEffect, useState, useRef, useCallback } from 'react';
import { WebSocketMetricEvent, RoundMetric } from '../types/training';
import { WS_BASE_URL } from '../api/client';

export function useMetricsSocket() {
  const [isConnected, setIsConnected] = useState<boolean>(false);
  const [lastEvent, setLastEvent] = useState<WebSocketMetricEvent | null>(null);
  const [eventsLog, setEventsLog] = useState<Array<{ time: string; type: string; message: string }>>([]);
  const [liveRounds, setLiveRounds] = useState<RoundMetric[]>([]);
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<number | null>(null);

  const connect = useCallback(() => {
    try {
      if (wsRef.current) {
        wsRef.current.close();
      }

      const socket = new WebSocket(WS_BASE_URL);
      wsRef.current = socket;

      socket.onopen = () => {
        setIsConnected(true);
        addLog('system', 'Connected to live WebSocket metrics stream');
        if (reconnectTimeoutRef.current) {
          clearTimeout(reconnectTimeoutRef.current);
          reconnectTimeoutRef.current = null;
        }
      };

      socket.onmessage = (event) => {
        try {
          const data: WebSocketMetricEvent = JSON.parse(event.data);
          setLastEvent(data);

          if (data.event === 'round_complete' && data.round && data.accuracy !== undefined && data.loss !== undefined) {
            const newMetric: RoundMetric = {
              id: Date.now(),
              runId: data.run_id || 'active_run',
              roundNumber: data.round,
              totalRounds: data.total_rounds || 5,
              accuracy: data.accuracy,
              loss: data.loss,
              epsilonSpent: data.epsilon_spent || 0.45,
              cumulativeEpsilon: data.cumulative_epsilon || 0.45,
              participatingOrgs: data.org_statuses ? Object.keys(data.org_statuses) : [],
              orgStatuses: data.org_statuses || {},
              durationSeconds: data.duration_seconds || 2.4,
              status: 'completed',
              timestamp: data.timestamp || new Date().toISOString(),
            };
            setLiveRounds((prev) => [...prev.filter((r) => r.roundNumber !== newMetric.roundNumber), newMetric]);
            addLog('round_complete', `Round ${data.round}/${data.total_rounds} | Acc: ${(data.accuracy * 100).toFixed(2)}% | Loss: ${data.loss.toFixed(4)} | +${(data.epsilon_spent || 0).toFixed(3)} ε`);
          } else if (data.event === 'training_started') {
            setLiveRounds([]);
            addLog('training_started', `${data.message || `Training started (${data.total_rounds} rounds)`}`);
          } else if (data.event === 'training_completed') {
            addLog('training_completed', `Training Completed. Final Accuracy: ${((lastEvent?.accuracy || 0.92) * 100).toFixed(2)}%`);
          } else if (data.event === 'training_stopped') {
            addLog('training_stopped', `Training halted.`);
          }
        } catch (err) {
          console.warn('Failed to parse WebSocket JSON:', err);
        }
      };

      socket.onerror = () => {
        setIsConnected(false);
      };

      socket.onclose = () => {
        setIsConnected(false);
        if (!reconnectTimeoutRef.current) {
          reconnectTimeoutRef.current = window.setTimeout(connect, 4000);
        }
      };
    } catch (e) {
      setIsConnected(false);
    }
  }, [lastEvent?.accuracy]);

  const addLog = (type: string, message: string) => {
    const time = new Date().toLocaleTimeString();
    setEventsLog((prev) => [{ time, type, message }, ...prev.slice(0, 40)]);
  };

  useEffect(() => {
    connect();
    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
    };
  }, [connect]);

  return {
    isConnected,
    lastEvent,
    liveRounds,
    eventsLog,
    clearLogs: () => setEventsLog([]),
  };
}
