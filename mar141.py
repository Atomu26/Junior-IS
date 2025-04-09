import os
import cv2
import numpy as np
from PIL import Image, ImageTk, ImageFilter
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

def apply_blur(image, blur_amount):
    """
    Apply a Gaussian blur effect to the image.
    :param image: PIL Image object
    :param blur_amount: Radius of the blur (higher values = more blur)
    :return: Blurred PIL Image object
    """
    return image.filter(ImageFilter.GaussianBlur(radius=blur_amount))

def apply_fog(image, fog_amount):
    """
    Apply a fog effect to the image by overlaying a semi-transparent white layer.
    :param image: PIL Image object
    :param fog_amount: Opacity of the fog (0 = no fog, 255 = fully opaque)
    :return: PIL Image object with fog effect
    """
    fog = Image.new("RGBA", image.size, (255, 255, 255, fog_amount))
    return Image.alpha_composite(image.convert("RGBA"), fog)

def merge_layers(layers, output_video, fps=30, blur_amount=0, fog_amount=0, blur_layers=None, fog_layers=None, progress_callback=None):
    """
    Merge multiple layers of images into a single video with optional blur and fog effects.
    :param layers: List of layers (each layer is a list of image paths)
    :param output_video: Path to the output video file
    :param fps: Frames per second for the output video
    :param blur_amount: Amount of blur to apply (0 = no blur)
    :param fog_amount: Amount of fog to apply (0 = no fog)
    :param blur_layers: List of layer indices to apply blur effect (empty for no blur)
    :param fog_layers: List of layer indices to apply fog effect (empty for no fog)
    :param progress_callback: Callback function to update progress
    """
    # Ensure all layers have the same number of images
    num_frames = max(len(layer) for layer in layers)  # Use the longest layer as the reference
    for i in range(len(layers)):
        if len(layers[i]) < num_frames:
            # Pad shorter layers by repeating the last frame
            layers[i] += [layers[i][-1]] * (num_frames - len(layers[i]))

    # Get the dimensions of the first image
    first_image = Image.open(layers[0][0])
    width, height = first_image.size

    # Initialize video writer
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # Codec for mp4
    video_writer = cv2.VideoWriter(output_video, fourcc, fps, (width, height))

    total_frames = num_frames
    for i in range(total_frames):
        # Start with the bottom layer (Layer 1)
        merged_image = Image.open(layers[0][i]).convert("RGBA")

        # Merge all layers on top
        for layer_index, layer in enumerate(layers[1:], start=1):
            layer_image = Image.open(layer[i]).convert("RGBA")

            # Apply blur effect to the selected layers
            if blur_layers and layer_index in blur_layers and blur_amount > 0:
                layer_image = apply_blur(layer_image, blur_amount)

            # Apply fog effect to the selected layers
            if fog_layers and layer_index in fog_layers and fog_amount > 0:
                layer_image = apply_fog(layer_image, fog_amount)

            merged_image = Image.alpha_composite(merged_image, layer_image)

        # Convert the merged image to BGR format for OpenCV
        merged_image_bgr = cv2.cvtColor(np.array(merged_image), cv2.COLOR_RGBA2BGR)

        # Write the frame to the video
        video_writer.write(merged_image_bgr)

        # Update progress
        if progress_callback:
            progress_callback((i + 1) / total_frames * 100)

    # Release the video writer
    video_writer.release()

class PNGtoMP4App:
    def __init__(self, root):
        self.root = root
        self.root.title("Sequence of PNG to MP4 Merger")
        #self.root.geometry("800x600")

        # Create a  scrollbar
        self.canvas_frame = tk.Frame(root)
        self.canvas_frame.pack(fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(self.canvas_frame, borderwidth=0)
        self.scrollbar = tk.Scrollbar(self.canvas_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")



         # Icon 
        try:
            icon = Image.open('360p.png')  
            photo = ImageTk.PhotoImage(icon)
            self.root.tk.call('wm', 'iconphoto', self.root._w, photo)
        except:
            pass # Passes if icon is not there.

        # Variables
        self.layers = []  # List of layers (each layer is a list of image paths)
        self.output_video = tk.StringVar()
        self.fps = tk.IntVar(value=30)
        self.blur_amount = tk.IntVar(value=0)
        self.fog_amount = tk.IntVar(value=0)
        self.blur_layers = []  # List of layer indices for blur effect
        self.fog_layers = []  # List of layer indices for fog effect
        self.merged_images = []  # Store merged images for preview
        self.current_frame = 0
        self.is_playing = False  # Track if preview is playing

        # Initialize GUI Elements
        self.layer_frames = []  # Frames for each layer's UI

        # Output and FPS
        tk.Label(self.scrollable_frame, text="Output Video File:").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        tk.Entry(self.scrollable_frame, textvariable=self.output_video, width=40).grid(row=0, column=1, padx=10, pady=10)
        tk.Button(self.scrollable_frame, text="Browse", command=self.browse_output).grid(row=0, column=2, padx=10, pady=10)

        tk.Label(self.scrollable_frame, text="FPS:").grid(row=1, column=0, padx=10, pady=10, sticky="w")
        tk.Entry(self.scrollable_frame, textvariable=self.fps, width=10).grid(row=1, column=1, padx=10, pady=10, sticky="w")

        # Blur and Fog Effects
        tk.Label(self.scrollable_frame, text="Blur Amount:").grid(row=2, column=0, padx=10, pady=10, sticky="w")
        self.blur_slider = ttk.Scale(self.scrollable_frame, from_=0, to=10, orient=tk.HORIZONTAL, variable=self.blur_amount)
        self.blur_slider.grid(row=2, column=1, padx=10, pady=10, sticky="w")

        tk.Label(self.scrollable_frame, text="Blur Layers:").grid(row=2, column=2, padx=10, pady=10, sticky="w")
        self.blur_layer_listbox = tk.Listbox(self.scrollable_frame, selectmode=tk.MULTIPLE)
        self.blur_layer_listbox.grid(row=2, column=3, padx=10, pady=10, sticky="w")

        tk.Label(self.scrollable_frame, text="Fog Amount:").grid(row=3, column=0, padx=10, pady=10, sticky="w")
        self.fog_slider = ttk.Scale(self.scrollable_frame, from_=0, to=255, orient=tk.HORIZONTAL, variable=self.fog_amount)
        self.fog_slider.grid(row=3, column=1, padx=10, pady=10, sticky="w")

        tk.Label(self.scrollable_frame, text="Fog Layers:").grid(row=3, column=2, padx=10, pady=10, sticky="w")
        self.fog_layer_listbox = tk.Listbox(self.scrollable_frame, selectmode=tk.MULTIPLE)
        self.fog_layer_listbox.grid(row=3, column=3, padx=10, pady=10, sticky="w")

        # Progress Bar
        self.progress = ttk.Progressbar(self.scrollable_frame, orient="horizontal", length=400, mode="determinate")
        self.progress.grid(row=4, column=0, columnspan=3, padx=10, pady=20)

        # Merge Button
        tk.Button(self.scrollable_frame, text="Merge and Create Video", command=self.start_merge).grid(row=5, column=0, columnspan=3, pady=10)

        # Timeline and Preview
        self.timeline_frame = tk.Frame(self.scrollable_frame)
        self.timeline_frame.grid(row=6, column=0, columnspan=3, padx=10, pady=10)
        self.timeline_label = tk.Label(self.timeline_frame, text="Timeline:")
        self.timeline_label.pack(side=tk.LEFT)
        self.timeline_slider = ttk.Scale(self.timeline_frame, from_=0, to=100, orient=tk.HORIZONTAL, command=self.update_preview)
        self.timeline_slider.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.preview_frame = tk.Frame(self.scrollable_frame)
        self.preview_frame.grid(row=7, column=0, columnspan=3, padx=10, pady=10)
        self.preview_label = tk.Label(self.preview_frame, text="Preview:")
        self.preview_label.pack()
        self.preview_canvas = tk.Canvas(self.preview_frame, width=400, height=300)
        self.preview_canvas.pack()

        # Play/Pause Button
        self.play_button = tk.Button(self.scrollable_frame, text="Play", command=self.toggle_play)
        self.play_button.grid(row=8, column=0, columnspan=3, pady=10)

        # Add/Remove Layer Buttons
        self.add_layer_button = tk.Button(self.scrollable_frame, text="Add Layer", command=self.add_layer_ui)
        self.add_layer_button.grid(row=9, column=0, pady=10)
        self.remove_layer_button = tk.Button(self.scrollable_frame, text="Remove Layer", command=self.remove_layer_ui)
        self.remove_layer_button.grid(row=9, column=1, pady=10)

        # Add initial layers (Layer 1 and Layer 2)
        self.add_layer_ui()
        self.add_layer_ui()
        self.bind_mousewheel()

        
    def bind_mousewheel(self): # Scroll using mouse 
        def _on_mousewheel(event):
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        self.canvas.bind_all("<MouseWheel>", _on_mousewheel)


    def add_layer_ui(self):
        """Add a new layer UI to the interface."""
        layer_index = len(self.layers) + 1
        layer_frame = tk.Frame(self.scrollable_frame)
        layer_frame.grid(row=10 + len(self.layers), column=0, columnspan=3, padx=10, pady=10)

        tk.Label(layer_frame, text=f"Layer {layer_index} (Folder or PNG):").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        layer_path = tk.StringVar()
        tk.Entry(layer_frame, textvariable=layer_path, width=40).grid(row=0, column=1, padx=10, pady=10)
        tk.Button(layer_frame, text="Browse", command=lambda: self.browse_layer(layer_path)).grid(row=0, column=2, padx=10, pady=10)

        self.layers.append([])  # Add an empty list for this layer's images
        self.layer_frames.append((layer_frame, layer_path))

        # Update the blur and fog layer listboxes
        self.update_layer_listboxes()

    def remove_layer_ui(self):
        """Remove the last layer UI from the interface."""
        if len(self.layers) > 1:  # Ensure at least one layer remains
            layer_frame, _ = self.layer_frames.pop()
            layer_frame.destroy()
            self.layers.pop()

            # Update the blur and fog layer listboxes
            self.update_layer_listboxes()

    def update_layer_listboxes(self):
        """Update the blur and fog layer listboxes when layers are added or removed."""
        self.blur_layer_listbox.delete(0, tk.END)
        self.fog_layer_listbox.delete(0, tk.END)
        for i in range(len(self.layers)):
            self.blur_layer_listbox.insert(tk.END, f"Layer {i + 1}")
            self.fog_layer_listbox.insert(tk.END, f"Layer {i + 1}")

    def browse_layer(self, layer_path_var):
        """Browse for a folder or PNG file for the layer."""
        path = filedialog.askopenfilename(filetypes=[("PNG files", "*.png")])
        if not path:
            path = filedialog.askdirectory()
        if path:
            layer_path_var.set(path)

    def browse_output(self):
        """Browse for the output video file."""
        file = filedialog.asksaveasfilename(defaultextension=".mp4", filetypes=[("MP4 files", "*.mp4")])
        if file:
            self.output_video.set(file)

    def start_merge(self):
        """Start merging layers and creating the video."""
        # Get all layer paths
        layers = []
        for _, layer_path_var in self.layer_frames:
            path = layer_path_var.get()
            if not path:
                messagebox.showerror("Error", "Please provide paths for all layers.")
                return

            if os.path.isfile(path) and path.endswith('.png'):
                # Single image for the layer
                layers.append([path])  # Add as a list with one image
            elif os.path.isdir(path):
                # Folder of images for the layer
                png_files = sorted([os.path.join(path, f) for f in os.listdir(path) if f.endswith('.png')])
                if not png_files:
                    messagebox.showerror("Error", f"The folder '{path}' contains no PNG files.")
                    return
                layers.append(png_files)
            else:
                raise ValueError("Layer must be a folder or a single PNG file.")

        # Ensure all layers have the same number of frames
        num_frames = max(len(layer) for layer in layers)  # Use the longest layer as the reference
        for i in range(len(layers)):
            if len(layers[i]) < num_frames:
                # Pad shorter layers by repeating the last frame
                layers[i] += [layers[i][-1]] * (num_frames - len(layers[i]))

        output_video = self.output_video.get()
        fps = self.fps.get()
        blur_amount = self.blur_amount.get()
        fog_amount = self.fog_amount.get()

        # Get selected layers for blur and fog effects
        blur_layers = [i for i in self.blur_layer_listbox.curselection()]
        fog_layers = [i for i in self.fog_layer_listbox.curselection()]

        if not output_video:
            messagebox.showerror("Error", "Please specify the output video file.")
            return

        try:
            def update_progress(percent):
                self.progress["value"] = percent
                self.root.update_idletasks()

            # Generate merged images for preview
            self.merged_images = self.generate_merged_images(layers, blur_amount, fog_amount, blur_layers, fog_layers)
            self.timeline_slider.config(to=len(self.merged_images) - 1)
            self.update_preview()

            # Merge and create video
            merge_layers(layers, output_video, fps, blur_amount, fog_amount, blur_layers, fog_layers, update_progress)
            messagebox.showinfo("Success", "Video created successfully!")
            self.progress["value"] = 0
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def generate_merged_images(self, layers, blur_amount, fog_amount, blur_layers, fog_layers):
        """Generate merged images for preview."""
        merged_images = []
        num_frames = len(layers[0])

        for i in range(num_frames):
            # Start with the bottom layer (Layer 1)
            merged_image = Image.open(layers[0][i]).convert("RGBA")

            # Merge all layers on top
            for layer_index, layer in enumerate(layers[1:], start=1):
                layer_image = Image.open(layer[i]).convert("RGBA")

                # Apply blur effect to the selected layers
                if layer_index in blur_layers and blur_amount > 0:
                    layer_image = apply_blur(layer_image, blur_amount)

                # Apply fog effect to the selected layers
                if layer_index in fog_layers and fog_amount > 0:
                    layer_image = apply_fog(layer_image, fog_amount)

                merged_image = Image.alpha_composite(merged_image, layer_image)

            merged_images.append(merged_image)

        return merged_images

    def update_preview(self, *args):
        """Update the preview window based on the timeline slider."""
        if not self.merged_images:
            return

        frame_index = int(self.timeline_slider.get())
        if frame_index < 0 or frame_index >= len(self.merged_images):
            return

        merged_image = self.merged_images[frame_index]
        merged_image.thumbnail((400, 300))  # Resize for preview
        photo = ImageTk.PhotoImage(merged_image)
        self.preview_canvas.create_image(0, 0, anchor=tk.NW, image=photo)
        self.preview_canvas.image = photo  # Keep a reference to avoid garbage collection

    def toggle_play(self):
        """Toggle play/pause for the preview."""
        if not self.merged_images:
            return

        self.is_playing = not self.is_playing
        if self.is_playing:
            self.play_button.config(text="Pause")
            self.play_preview()
        else:
            self.play_button.config(text="Play")

    def play_preview(self):
        """Play the preview at the specified FPS."""
        if not self.is_playing:
            return

        # Update the current frame
        self.current_frame = (self.current_frame + 1) % len(self.merged_images)
        self.timeline_slider.set(self.current_frame)
        self.update_preview()

        # Schedule the next frame
        delay = int(1000 / self.fps.get())  # Convert FPS to milliseconds
        self.root.after(delay, self.play_preview)

if __name__ == "__main__":
    root = tk.Tk()
    app = PNGtoMP4App(root)
    root.mainloop()
