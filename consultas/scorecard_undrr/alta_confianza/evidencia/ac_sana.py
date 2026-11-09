# Saná (Secretaría de la Capital): base de alta confianza, búsqueda nov-2026.
ID, NOMBRE, ISO3 = 'sana', 'Saná', 'YEM'
OFICINA = 'Defensa Civil de Saná / Secretaría de la Capital'
C, M = 'alta', 'media'
CORTO, MED, LARGO = 'Corto plazo (≤1 año)', 'Mediano plazo (1-3 años)', 'Largo plazo (>3 años)'

F = {
    'daraj': ('https://daraj.media/en/yemen-floods-wash-away-the-old-houses-of-sanaa-and-the-state-is-absent/', 'Daraj: las inundaciones arrasan las casas antiguas de Saná y el Estado está ausente', 's/f'),
    'newarab': ('https://newarab.com/news/10-historic-buildings-collapse-sanaa-due-heavy-rains', 'The New Arab: diez edificios históricos colapsan en Saná por lluvias intensas', 's/f'),
}

EN = {
    '1.2.2': (1, M, 'Con las lluvias, casas y edificios históricos de la ciudad vieja colapsan y la prensa describe la ausencia del Estado; la defensa civil solo publica balances. No se informa un proceso de coordinación de la respuesta.',
        'daraj,newarab', 'Iniciar un proceso de coordinación de la respuesta.', 'Defensa Civil / Secretaría de la Capital', CORTO),
}
ES = {
}
