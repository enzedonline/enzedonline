// js/embed-external-link-blocks.js

class ExternalLinkEmbedBlockDefinition extends window.wagtailStreamField.blocks
    .StructBlockDefinition {
    render(placeholder, prefix, initialState, initialError) {
        const block = super.render(
            placeholder,
            prefix,
            initialState,
            initialError,
        );

        const updateImagePreview = async () => {
            const imageUrl = block.imageInput.value;
            if (imageUrl) {
                try {
                    const response = await fetch(`/check-image-url/?url=${encodeURIComponent(imageUrl)}`);
                    const data = await response.json();
                    if (data.valid) {
                        block.imagePreview.innerHTML = `<img src="${imageUrl}" alt="Image Preview" class="external-link-embed-block-image-preview">`;
                    } else {
                        block.imagePreview.innerHTML = '<p class="error-message">Failed to load image<p>';
                    }
                } catch (error) {
                    block.imagePreview.innerHTML = '';
                    console.error('Error checking image URL:', error);
                }
            } else {
                block.imagePreview.innerHTML = '';
            }
        }

        const getMetadata = async () => {
            const url = block.externalLinkInput.value;

            if (url) {
                try {
                    block.getMetadataButton.classList.toggle('spinner', true);
                    const response = await fetch(`/external-content-proxy/?url=${encodeURIComponent(url)}`);
                    const metadata = await response.json();

                    // Handle metadata error
                    block.externalLinkErrors.innerText = metadata.error || '';
                    if (metadata.error) {
                        block.externalLinkErrors.classList.add('error-message');
                    } else {
                        block.externalLinkErrors.classList.remove('error-message');
                    }

                    // Update url with resolved address
                    if (!metadata.error) {
                        block.externalLinkInput.value = metadata.url;
                    }

                    // Add title as h3 heading and description to RichTextBlock
                    const rtbState = block.childBlocks.description.getState();
                    const blocksFromHTML = DraftJS.convertFromHTML(
                        (metadata.title ? `<h5>${metadata.title}</h5>` : '') + 
                        (metadata.description || '')
                    );
                    block.childBlocks.description.setState(new rtbState.constructor.createWithContent(
                        new rtbState._immutable.currentContent.constructor.createFromBlockArray(
                            blocksFromHTML.contentBlocks,
                            blocksFromHTML.entityMap,
                            )
                        )
                    );

                    block.imageInput.value = metadata.image || '';
                    updateImagePreview(); // Update image preview after changing imageInput

                } catch (error) {
                    console.error('Error retrieving metadata:', error);
                }
                block.getMetadataButton.classList.toggle('spinner', false);
            }
        }

        const createImagePreview = () => {
            block.imagePreview = document.createElement('div');
            block.imageInput.parentNode.insertBefore(block.imagePreview, block.imageInput.nextSibling);
            block.imageInput.addEventListener('input', () => updateImagePreview());

            // Initialize image preview if imageInput has a value
            updateImagePreview();
        }

        const initialiseBlock = () => {

            block.externalLinkInput = document.getElementById(prefix + '-external_link')
            block.externalLinkErrors = document.getElementById(prefix + '-external_link-errors')
            block.imageInput = document.getElementById(prefix + '-image')
            block.titleInput = document.getElementById(prefix + '-title')
            block.descriptionInput = document.getElementById(prefix + '-description')

            const container = document.createElement('div');
            container.className = 'external-link-embed-block-metadata-container';

            const errorMessage = document.createElement('span');
            errorMessage.className = 'external-link-embed-block-metadata-error';

            const button = document.createElement('button');
            button.className = 'button button-small button-secondary metadata-button';
            button.textContent = 'Get Metadata';
            button.addEventListener('click', (event) => {
                event.preventDefault();
                getMetadata();
            });
            container.appendChild(errorMessage);
            container.appendChild(button);

            // Append the container to the parent element
            block.externalLinkInput.parentNode.insertBefore(container, block.externalLinkInput.nextSibling);

            // Assign the elements to class properties
            block.externalLinkErrors = errorMessage;
            block.getMetadataButton = button;
            createImagePreview();

        }

        initialiseBlock(prefix);
        return block;
    }


}

window.telepath.register('blocks.models.ExternalLinkEmbedBlock', ExternalLinkEmbedBlockDefinition);
