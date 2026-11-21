import { Injectable } from '@nestjs/common';
import { PrestadoresRepository } from './prestadores.repository';

@Injectable()
export class PrestadoresService {
  constructor(private readonly repo: PrestadoresRepository) {}

  buscarPorId(id: string) {
    return this.repo.buscarPorId(id);
  }
}
