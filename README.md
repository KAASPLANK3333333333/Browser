name: Package Windows Release

on:
  workflow_dispatch:
    inputs:
      tag:
        description: 'Release tag to create (e.g. v1.0.0)'
        required: true
        default: 'v1.0.0'
  push:
    tags:
      - 'v*'

jobs:
  build-and-release:
    runs-on: windows-latest

    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Install 7-Zip
        run: |
          choco install 7zip -y

      - name: Create zip of repository (exclude .git)
        run: |
          powershell -Command "Compress-Archive -Path (Get-ChildItem -Path . -Force | Where-Object { $_.Name -ne '.git' }) -DestinationPath repo-${{ github.event_name == 'push' && github.ref_name || github.event.inputs.tag }}.zip"

      - name: Create self-extracting EXE using 7z
        run: |
          7z a -sfx repo-${{ github.event_name == 'push' && github.ref_name || github.event.inputs.tag }}.exe repo-${{ github.event_name == 'push' && github.ref_name || github.event.inputs.tag }}.zip

      - name: Create GitHub Release
        id: create_release
        uses: actions/create-release@v1
        with:
          tag_name: ${{ github.event_name == 'push' && github.ref_name || github.event.inputs.tag }}
          release_name: ${{ github.event_name == 'push' && github.ref_name || github.event.inputs.tag }}
          draft: false
          prerelease: false
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}

      - name: Upload release asset (EXE)
        uses: actions/upload-release-asset@v1
        with:
          upload_url: ${{ steps.create_release.outputs.upload_url }}
          asset_path: repo-${{ github.event_name == 'push' && github.ref_name || github.event.inputs.tag }}.exe
          asset_name: browser-${{ github.event_name == 'push' && github.ref_name || github.event.inputs.tag }}.exe
          asset_content_type: application/octet-stream
