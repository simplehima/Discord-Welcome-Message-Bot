import os
import requests
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import discord
from discord import Intents
from discord.ext import commands
import imageio
from PIL import Image, ImageDraw, ImageFont, ImageSequence
import numpy as np  
intents = Intents.default()

intents.members = True
client = commands.Bot(command_prefix='!', intents=intents)


@client.event
async def on_ready():
    print('Bot is ready!')

async def create_welcome_image(user, background_gif_path):
    # Download user's avatar
    avatar_url = str(user.display_avatar.url)
    response = requests.get(avatar_url)
    user_avatar = Image.open(BytesIO(response.content))

    # Ensure the user avatar has an alpha channel
    user_avatar = user_avatar.convert("RGBA")

    # Resize the user_avatar to desired dimensions (width, height)
    desired_avatar_size = (80, 80)
    user_avatar.thumbnail(desired_avatar_size, Image.LANCZOS)

    # Create a circular mask for the avatar
    avatar_size = user_avatar.size[0]  # Update the avatar_size variable
    mask = Image.new("L", (avatar_size, avatar_size), 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0, avatar_size, avatar_size), fill=255)

    # Apply the circular mask to the avatar
    user_avatar.putalpha(mask)

    # Open background GIF
    background_gif = Image.open(background_gif_path)

    # Prepare a list to store the frames of the new GIF
    new_frames = []

    # Specify the (x, y) coordinates for the top-left corner of the avatar on the frame
    avatar_position = (311, 60 )  # Change these values to adjust the position

    # Iterate through the frames of the background GIF
    for frame in ImageSequence.Iterator(background_gif):
        # Convert the frame to RGBA mode
        frame_rgba = frame.convert("RGBA")

        # Create a mask from the user avatar's alpha channel
        avatar_mask = user_avatar.getchannel("A")

        # Paste user's avatar on the frame using the mask and the specified position
        frame_rgba.paste(user_avatar, avatar_position, avatar_mask)

        # Add user's name to the frame
        draw = ImageDraw.Draw(frame_rgba)
        font = ImageFont.truetype("arial.ttf", 30)  # Choose a font and size
        draw.text((200, 3), f"Welcome, {user.name}!", font=font)

        # Add the modified frame to the new_frames list
        new_frames.append(frame_rgba)

    # Save the new GIF using imageio
    with imageio.get_writer("welcome.gif", mode="I", duration=background_gif.info["duration"] / 1000) as writer:
        for frame in new_frames:
            # Convert the PIL Image object to a NumPy array
            frame_np = np.array(frame)
            writer.append_data(frame_np)

    return "welcome.gif"

@client.event
async def on_member_join(member):
    # Find the 'welcome' channel in the server
    welcome_channel = None
    for channel in member.guild.text_channels:
        if channel.name == '👋・joins-leaves':
            welcome_channel = channel
            break

    # Create the channel if it doesn't exist
    if welcome_channel is None:
        overwrites = {member.guild.default_role: discord.PermissionOverwrite(read_messages=False)}
        welcome_channel = await member.guild.create_text_channel('👋・joins-leaves', overwrites=overwrites)

    # Create the welcome GIF
    welcome_gif_path = await create_welcome_image(member, "background.gif")

    # Send the welcome message and the GIF to the 'welcome' channel
    await welcome_channel.send(f"Welcome to the server, {member.mention}!", file=discord.File(welcome_gif_path))

client.run('bot token here')