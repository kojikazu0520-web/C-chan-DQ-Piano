$envFile = Get-Content .env
$apiKey = $null

foreach ($line in $envFile) {
  if ($line -match '^YOUTUBE_API_KEY=(.+)$') {
    $apiKey = $matches[1]
  }
}

if (-not $apiKey) {
  throw "YOUTUBE_API_KEY was not found in .env"
}

$channelId = "UCso4vdUt3Pq3MD-6y1qdQRw"
$playlistsUrl = "https://www.googleapis.com/youtube/v3/playlists?part=snippet,contentDetails&channelId=$channelId&maxResults=50&key=$apiKey"
$response = Invoke-RestMethod -Uri $playlistsUrl

$playlists = $response.items | ForEach-Object {
  [PSCustomObject]@{
    id = $_.id
    title = $_.snippet.title
    description = $_.snippet.description
    thumbnail = if ($_.snippet.thumbnails.maxres.url) {
      $_.snippet.thumbnails.maxres.url
    } elseif ($_.snippet.thumbnails.standard.url) {
      $_.snippet.thumbnails.standard.url
    } elseif ($_.snippet.thumbnails.high.url) {
      $_.snippet.thumbnails.high.url
    } else {
      $_.snippet.thumbnails.medium.url
    }
    itemCount = $_.contentDetails.itemCount
    publishedAt = $_.snippet.publishedAt
    url = "https://www.youtube.com/playlist?list=$($_.id)"
  }
}

$json = $playlists | ConvertTo-Json -Depth 5
"window.playlistData = $json;" | Set-Content -Encoding UTF8 playlist-data.js
