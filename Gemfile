source "https://rubygems.org"

# Remove explicit Jekyll and minima versions
gem "github-pages", group: :jekyll_plugins
gem "jekyll-remote-theme"
gem "webrick"
gem "faraday-retry"
gem "public_suffix", "~> 5.1.1"  # Add specific version for compatibility

group :jekyll_plugins do
  gem "jekyll-seo-tag"
end

# Add this line to ensure platform consistency
platforms :mingw, :x64_mingw, :mswin, :jruby do
  gem "tzinfo", "~> 1.2"
  gem "tzinfo-data"
end