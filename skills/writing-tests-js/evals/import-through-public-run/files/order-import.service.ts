export interface Order {
  id: string;
  totalCents: number;
  currency: string;
}

export interface RawOrder {
  id: string | number;
  total: string | number;
  currency?: string;
  status?: string;
}

/** HTTP client for the partner API. */
export interface PartnerClient {
  fetchOrders(since: string): Promise<RawOrder[]>;
}

/** Database repository. */
export interface OrderRepository {
  exists(orderId: string): Promise<boolean>;
  saveMany(orders: Order[]): Promise<void>;
}

export interface ImportResult {
  fetched: number;
  saved: number;
  skipped: number;
}

export class OrderImportService {
  constructor(
    private readonly client: PartnerClient,
    private readonly repo: OrderRepository,
  ) {}

  async run(since: string): Promise<ImportResult> {
    const raw = await this.client.fetchOrders(since);
    const orders = raw.filter((r) => r.status !== 'cancelled').map((r) => this.normalize(r));
    const fresh: Order[] = [];
    for (const order of orders) {
      if (!(await this.repo.exists(order.id))) fresh.push(order);
    }
    if (fresh.length > 0) await this.repo.saveMany(fresh);
    return { fetched: raw.length, saved: fresh.length, skipped: raw.length - fresh.length };
  }

  private normalize(raw: RawOrder): Order {
    return {
      id: String(raw.id).trim(),
      totalCents: Math.round(Number(raw.total) * 100),
      currency: (raw.currency ?? 'BRL').toUpperCase(),
    };
  }
}
