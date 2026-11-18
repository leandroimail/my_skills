export type Region = 'south' | 'southeast' | 'north';

const BASE_FEE: Record<Region, number> = { south: 15, southeast: 10, north: 30 };
const FREE_SHIPPING_THRESHOLD = 300;
const EXTRA_KG_FEE = 2.5;
const INCLUDED_KG = 5;
const MAX_FEE = 80;

/** Returns the shipping fee in BRL for an order. */
export function calculateShipping(subtotal: number, weightKg: number, region: Region): number {
  if (subtotal < 0 || weightKg <= 0) {
    throw new RangeError('subtotal must be >= 0 and weightKg must be > 0');
  }
  if (subtotal >= FREE_SHIPPING_THRESHOLD && region !== 'north') {
    return 0;
  }
  const extraKg = Math.max(0, Math.ceil(weightKg - INCLUDED_KG));
  const fee = BASE_FEE[region] + extraKg * EXTRA_KG_FEE;
  return Math.min(fee, MAX_FEE);
}
