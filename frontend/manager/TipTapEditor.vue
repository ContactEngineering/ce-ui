<script setup>
import { ref, onMounted, onBeforeUnmount, watch } from 'vue'
import { Editor, EditorContent } from '@tiptap/vue-3'
import StarterKit from '@tiptap/starter-kit'
import Underline from '@tiptap/extension-underline'



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
  <div v-if="editor" class="container">
    <!-- Toolbar -->
    <div class="toolbar">
        <button 
            @click="editor.chain().focus().toggleBold().run()" 
            :class="{ 'is-active': editor.isActive('bold') }"
            :disabled="disabled"
        >
        Bold
        </button>
        <button 
            @click="editor.chain().focus().toggleItalic().run()" 
            :class="{ 'is-active': editor.isActive('italic') }"
            :disabled="disabled"
        >
        Italic
        </button>
        <button 
            @click="editor.chain().focus().toggleUnderline().run()" 
            :class="{ 'is-active': editor.isActive('underline') }"
            :disabled="disabled"
        >
        Underline
        </button>
        <button
          @click="editor.chain().focus().toggleBulletList().run()"
          :class="{ 'is-active': editor.isActive('bulletList') }"
          :disabled="disabled"
        >
          Bullet list
        </button>
    </div>

    <!-- Editor -->
    <editor-content class="tiptap" :class="{ 'is-disabled': disabled }" :editor="editor" :disabled="disabled"/>
  </div>
</template>

<style scoped>
.container {
  border: 1px solid #ccc;
  padding: 1rem;
  min-height: 150px;
}

.toolbar {
  margin-top: 0.5rem;
  margin-bottom: 0.5rem;
}

button {
  margin-right: 0.3rem;
  padding: 0.3rem 0.6rem;
  border: 1px solid #d0d0d0;   
  border-radius: 4px;          
  background: #f9f9f9; 
}

button.is-active {
  background: #0F52BA;
  color: white;
}

button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.tiptap {
  background: #ffffff;
  min-height: 100px;
  padding: 0.5rem;
  border: 1px solid #ddd;
}

.tiptap.is-disabled {
  background: #f5f5f5;
  min-height: 100px;
  padding: 0.5rem;
  border: 1px solid #ddd;
}
</style>
