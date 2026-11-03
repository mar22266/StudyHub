import { hasValidTimeRange } from '../src/utils/appointment'

describe('horario de una sesión', () => {
  test('acepta una sesión que termina después de empezar', () => {
    expect(hasValidTimeRange('15:00', '16:30')).toBe(true)
  })

  test('rechaza inicio y fin iguales', () => {
    expect(hasValidTimeRange('15:00', '15:00')).toBe(false)
  })

  test('rechaza horarios invertidos o mal formados', () => {
    expect(hasValidTimeRange('16:30', '15:00')).toBe(false)
    expect(hasValidTimeRange('25:00', '26:00')).toBe(false)
  })
})
