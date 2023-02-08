def init_django():
  import django
  from django.conf import settings

  if settings.configured:
    return

  settings.configure(
    INSTALLED_APPS=[
        'cspr_summarization_block',
    ],
    DATABASES = {
    'default': {
      'ENGINE': 'django.db.backends.postgresql',
      'NAME': 'casper_aggregator_db',
      'USER': 'postgres',
      'PASSWORD': 'postgres',
      'HOST': 'localhost',
      'PORT': '5432',
    }
  }
  )
  django.setup()


if __name__ == "__main__":
  from django.core.management import execute_from_command_line

  init_django()
  execute_from_command_line()