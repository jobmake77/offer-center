export type Envelope<T> = {
  data: T;
  meta: Record<string, unknown>;
  error: {
    code: string;
    message: string;
    details: Record<string, unknown>;
  } | null;
};

