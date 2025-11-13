from app import app

print('Testing app import...')
print('✓ App loaded successfully')
print(f'\nRegistered routes:')
for route in app.routes:
    if hasattr(route, 'path') and hasattr(route, 'methods'):
        print(f'  {list(route.methods)} {route.path}')
