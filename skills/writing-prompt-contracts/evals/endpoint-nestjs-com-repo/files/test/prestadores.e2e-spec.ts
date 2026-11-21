import * as request from 'supertest';
import { criarApp, tokenCom } from './helpers';

describe('GET /prestadores/:id', () => {
  it('retorna 404 para prestador inexistente', async () => {
    const app = await criarApp();
    await request(app.getHttpServer())
      .get('/prestadores/999999')
      .set('Authorization', `Bearer ${tokenCom(['atendimento'])}`)
      .expect(404);
  });
});
