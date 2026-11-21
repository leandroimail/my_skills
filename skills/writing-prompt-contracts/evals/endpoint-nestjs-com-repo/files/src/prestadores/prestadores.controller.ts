import { Controller, Get, NotFoundException, Param, UseGuards } from '@nestjs/common';
import { JwtAuthGuard } from '../auth/jwt-auth.guard';
import { Roles } from '../auth/roles.decorator';
import { PrestadoresService } from './prestadores.service';

@Controller('prestadores')
@UseGuards(JwtAuthGuard)
export class PrestadoresController {
  constructor(private readonly service: PrestadoresService) {}

  @Get(':id')
  @Roles('atendimento')
  async buscar(@Param('id') id: string) {
    const prestador = await this.service.buscarPorId(id);
    if (!prestador) throw new NotFoundException({ code: 'PRESTADOR_NAO_ENCONTRADO', message: 'Prestador não encontrado' });
    return prestador;
  }
}
