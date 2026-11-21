import { Module } from '@nestjs/common';
import { PrestadoresController } from './prestadores.controller';
import { PrestadoresService } from './prestadores.service';
import { PrestadoresRepository } from './prestadores.repository';

@Module({
  controllers: [PrestadoresController],
  providers: [PrestadoresService, PrestadoresRepository],
})
export class PrestadoresModule {}
