# Define the default values
default_provider := '"royal road"'
default_output_dir := "${BOOKS_HOME}"

# Download a novel with optional provider, custom name and URL
download novel_name novel_url provider=default_provider:
    uv run python -m novel_scrapers download --provider {{provider}} \
    --novel-name "{{novel_name}}" --novel-url "{{novel_url}}" --output-dir {{default_output_dir}}/{{novel_name}}