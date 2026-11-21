import { Injectable } from '@nestjs/common';
import { OracleService } from '../database/oracle.service';

@Injectable()
export class PrestadoresRepository {
  constructor(private readonly db: OracleService) {}

  async buscarPorId(id: string) {
    const rows = await this.db.query(
      'SELECT CD_PRESTADOR, NM_PRESTADOR, FL_ATIVO FROM TB_PRESTADOR WHERE CD_PRESTADOR = :id',
      { id },
    );
    return rows[0] ?? null;
  }
}
