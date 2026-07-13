"""Provider de sensores para prácticas de Sistemas Programables.

Genera lecturas físicamente plausibles: rangos reales del sensor y ruido
gaussiano moderado, para que a simple vista no se distinga que son sintéticas.

Uso en un script:
    from faker import Faker
    from providers.sensores import SensorProvider

    fake = Faker("es_MX")
    fake.add_provider(SensorProvider)
    Faker.seed(2026)
    print(fake.temperatura_c(), fake.humedad_pct(), fake.id_dispositivo())

Uso desde el CLI (desde la raíz del repo; PYTHONPATH para que encuentre el módulo):
    PYTHONPATH=. faker -i providers.sensores temperatura_c
"""

from faker.providers import BaseProvider


class SensorProvider(BaseProvider):
    """Lecturas de sensores comunes en los kits de la materia (DHT22, MPU6050…)
    montados en Raspberry Pi Pico W / Pico 2 W, físicos o simulados en Wokwi."""

    def temperatura_c(self, base: float = 24.0, ruido: float = 0.6) -> float:
        """Temperatura ambiente en °C: `base` con ruido gaussiano `ruido` (σ)."""
        return round(base + self.generator.random.gauss(0, ruido), 2)

    def humedad_pct(self, base: float = 55.0, ruido: float = 2.0) -> float:
        """Humedad relativa en %, acotada al rango físico 0–100."""
        valor = base + self.generator.random.gauss(0, ruido)
        return round(min(100.0, max(0.0, valor)), 1)

    def aceleracion_g(self, ruido: float = 0.02) -> tuple:
        """(x, y, z) en g de un MPU6050 en reposo: z ≈ 1 g (gravedad)."""
        g = self.generator.random.gauss
        return (round(g(0, ruido), 3), round(g(0, ruido), 3), round(1.0 + g(0, ruido), 3))

    def id_dispositivo(self, modelo: str | None = None) -> str:
        """ID estilo Raspberry Pi Pico, p. ej. 'PICO2W-3FA9BC'.

        `modelo`: 'PICOW' o 'PICO2W'; si se omite, se elige al azar (sembrado).
        """
        if modelo is None:
            modelo = self.random_element(("PICOW", "PICO2W"))
        return self.hexify(f"{modelo}-^^^^^^").upper()

    def mac_pico(self) -> str:
        """MAC con OUI real de Raspberry Pi (28:cd:c1), como un Pico W físico."""
        return self.hexify("28:cd:c1:^^:^^:^^")

    def bateria_pct(self) -> int:
        """Nivel de batería 5–100 % (nunca 0: un nodo muerto no transmite)."""
        return self.random_int(5, 100)


# Alias que el CLI de faker (-i) espera encontrar: una clase llamada Provider.
Provider = SensorProvider
