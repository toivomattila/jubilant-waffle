
Confidence:
- Support for tagging image multiple times, not skipping if already tagged
- Would just add more tags
- Add a counter of how many times an image has been run through the tagger
- Add a counter for each tag on how many times it was tagged for an image
- Add a percentage of how often a tag was used for an image (tagged for this image count / total image went through tagger count)
- Let the user choose the confidence threshold for a tag to be used

Split tags with multiple words:
- "A cat with a hat" -> "Cat", "Hat" (remove fillwords like "A", and "with")

Image hover metadata such as tags etc

Tag(s) has been selected in the UI:
- Only show the tags that are available for the filtered images
- I.e. Filtered for a tag that returned only 1 image. Now I can still filter with all tags, resulting in 0 images in so many cases.
- Instead I'd like to filter with a broad tag & then narrow down with more specific tags

Show item count in the UI for each tag:
- "If I filter the images with this tag, how many images will I get?"
- I have no idea how computationally expensive this is to implement
