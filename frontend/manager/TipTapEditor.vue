<script setup>
import { ref, onMounted, onBeforeUnmount, watch } from 'vue'
import { Editor, EditorContent } from '@tiptap/vue-3'
import StarterKit from '@tiptap/starter-kit'
import Underline from '@tiptap/extension-underline'
import { QBtn, QBtnGroup } from 'quasar'

// Props: modelValue for v-model, disabled for read-only
const props = defineProps({
  modelValue: { type: String, default: '' },
  disabled: { type: Boolean, default: false },
})

const emit = defineEmits(['update:modelValue'])

const editor = ref(null)

onMounted(() => {
  editor.value = new Editor({
    extensions: [StarterKit, Underline],
    content: props.modelValue || '<p></p>',
    editable: !props.disabled,
    editorProps: {
      attributes: {
        placeholder: 'Start typing here...',
      },
    },
    onUpdate({ editor }) {
      emit('update:modelValue', editor.getHTML())
    },
  })
})

// Watch for external modelValue changes
watch(() => props.modelValue, (newVal) => {
  if (editor.value && newVal !== editor.value.getHTML()) {
    editor.value.commands.setContent(newVal)
  }
})

// Watch for disabled changes
watch(() => props.disabled, (newVal) => {
  if (editor.value) editor.value.setEditable(!newVal)
})

onBeforeUnmount(() => {
  if (editor.value) editor.value.destroy()
})
</script>

<template>
  <div v-if="editor" class="tiptap-container">
    <!-- Toolbar -->
    <QBtnGroup class="toolbar q-mb-sm" flat>
      <QBtn
        size="sm"
        flat
        class="btn-small"
        icon="format_bold"
        :color="editor.isActive('bold') ? 'primary' : undefined"
        :disable="disabled"
        @click="editor.chain().focus().toggleBold().run()"
        title="Bold"
      />

      <QBtn
        size="sm"
        flat
        class="btn-small"
        icon="format_italic"
        :color="editor.isActive('italic') ? 'primary' : undefined"
        :disable="disabled"
        @click="editor.chain().focus().toggleItalic().run()"
        title="Italic"
      />

      <QBtn
        size="sm"
        flat
        class="btn-small"
        icon="format_underlined"
        :color="editor.isActive('underline') ? 'primary' : undefined"
        :disable="disabled"
        @click="editor.chain().focus().toggleUnderline().run()"
        title="Underline"
      />

      <QBtn
        size="sm"
        flat
        class="btn-small"
        icon="format_list_bulleted"
        :color="editor.isActive('bulletList') ? 'primary' : undefined"
        :disable="disabled"
        @click="editor.chain().focus().toggleBulletList().run()"
        title="Bullet List"
      />

      <QBtn
        size="sm"
        flat
        class="btn-small"
        :color="editor.isActive('heading', { level: 1 }) ? 'primary' : undefined"
        :disable="disabled"
        @click="editor.chain().focus().toggleHeading({ level: 1 }).run()"
        title="Heading 1"
        label="H1"
      />

      <QBtn
        size="sm"
        flat
        class="btn-small"
        :color="editor.isActive('heading', { level: 2 }) ? 'primary' : undefined"
        :disable="disabled"
        @click="editor.chain().focus().toggleHeading({ level: 2 }).run()"
        title="Heading 2"
        label="H2"
      />

      <QBtn
        size="sm"
        flat
        class="btn-small"
        :color="editor.isActive('heading', { level: 3 }) ? 'primary' : undefined"
        :disable="disabled"
        @click="editor.chain().focus().toggleHeading({ level: 3 }).run()"
        title="Heading 3"
        label="H3"
      />

      <QBtn
        size="sm"
        flat
        class="btn-small"
        icon="format_clear"
        :disable="disabled"
        @click="editor.chain().focus().clearNodes().unsetAllMarks().run()"
        title="Clear formatting"
      />
    </QBtnGroup>

    <!-- Editor -->
    <editor-content
      class="tiptap"
      :editor="editor"
      :class="{ 'is-disabled': disabled }"
    />
  </div>
</template>

<style scoped>
.tiptap-container {
  border: 1px solid #ccc;
  padding: 1rem;
  min-height: 200px;
  border-radius: 6px;
  background: #fff;
}

.toolbar {
  display: flex;
  flex-wrap: wrap;
  gap: 0.4rem; /* spacing between buttons */
}

.btn-small {
  min-width: 32px; /* reduce width */
  padding: 0.2rem 0.35rem; /* smaller padding */
  font-size: 0.85rem; /* smaller text or icon */
  display: flex;
  align-items: center;
  justify-content: center;
}

.tiptap {
  background: #ffffff;
  min-height: 150px;
  padding: 0.5rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  line-height: 1.4;
  outline: none;
}

.tiptap.is-disabled {
  background: #f5f5f5;
}
</style>
