import { ApiError, errorMessage } from '../src/utils/apiError'

function responseError(detail: unknown): ApiError {
  return new ApiError(422, { detail })
}

describe('mensajes de error de la API', () => {
  test('muestra el detalle textual del backend', () => {
    expect(errorMessage(responseError('No tienes permiso'))).toBe('No tienes permiso')
  })

  test('extrae y limpia un error de validación de Pydantic', () => {
    expect(errorMessage(responseError([{ msg: 'Value error, Descripción inválida' }]))).toBe('Descripción inválida')
  })

  test('usa un mensaje seguro para errores inesperados', () => {
    expect(errorMessage(new Error('token interno'))).toBe('No fue posible completar la operación')
    expect(errorMessage(responseError([]))).toBe('No fue posible completar la operación')
  })
})
