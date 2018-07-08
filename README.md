# mediaTimelineRenderer

Render media files (video or audio) to image (png) timeline strips.

This is used as an optional component of [superLimitBreak/stageViewer](https://github.com/superLimitBreak/stageViewer)


## Description
* `/media/` input files
    * `video.mp4` (mtime 1234)
    * `audio.mp3` (mtime 5678)
* `/media/` output files
    * `video.mp4.png` (mtime 1234)
    * `audio.mp3.png` (mtime 5678)

Optimisation: If the `mtimes` of the source and destination file match, there is no need to process the file

## Configuration

* output image format (jpg or png)
* output image height
* pixels per second
    * from this frame extraction time from video is derived
* watch daemon time (seconds)
    * If absent just process and exit
    * If present `file_diff_scan` at duration to reprocess media

## Future Features

* Possible output of `x2` and `x4` images for retina displays?
