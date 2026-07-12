type MessageHandler = (data: unknown) => void;

const WS_BASE_URL = import.meta.env.VITE_WS_BASE_URL ?? "/ws";

function resolveWsUrl(path: string): string {
  const proto = window.location.protocol === "https:" ? "wss:" : "ws:";
  const base = WS_BASE_URL.startsWith("ws") ? WS_BASE_URL : `${proto}//${window.location.host}${WS_BASE_URL}`;
  const token = localStorage.getItem("access_token") ?? "";
  return `${base}${path}?token=${encodeURIComponent(token)}`;
}

export class ReconnectingSocket {
  private ws: WebSocket | null = null;
  private closedByUser = false;
  private retryDelayMs = 1000;
  private readonly maxRetryDelayMs = 15000;

  constructor(
    private readonly path: string,
    private readonly onMessage: MessageHandler,
    private readonly onStatusChange?: (connected: boolean) => void,
  ) {}

  connect(): void {
    this.closedByUser = false;
    const url = resolveWsUrl(this.path);
    this.ws = new WebSocket(url);

    this.ws.onopen = () => {
      this.retryDelayMs = 1000;
      this.onStatusChange?.(true);
    };

    this.ws.onmessage = (event) => {
      try {
        this.onMessage(JSON.parse(event.data));
      } catch {
        // ignore malformed frames
      }
    };

    this.ws.onclose = () => {
      this.onStatusChange?.(false);
      if (!this.closedByUser) {
        setTimeout(() => this.connect(), this.retryDelayMs);
        this.retryDelayMs = Math.min(this.retryDelayMs * 2, this.maxRetryDelayMs);
      }
    };

    this.ws.onerror = () => {
      this.ws?.close();
    };
  }

  close(): void {
    this.closedByUser = true;
    this.ws?.close();
  }
}
