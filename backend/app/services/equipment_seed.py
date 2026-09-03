"""Seed script for 14 diverse lab and club equipment items.

Uploads images from `app/services/images/` to Cloudinary (if present)
and persists equipment records to the database.

Run directly via:
    uv run python -m app.services.equipment_seed
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import SessionLocal
from app.models.inventory import Equipment
from app.utils.enums import EquipmentCategory

IMAGES_DIR = Path(__file__).parent / "images"

# Configure Cloudinary if credentials are present
try:
    import cloudinary
    import cloudinary.uploader

    if settings.CLOUDINARY_CLOUD_NAME and settings.CLOUDINARY_API_KEY and settings.CLOUDINARY_API_SECRET:
        cloudinary.config(
            cloud_name=settings.CLOUDINARY_CLOUD_NAME,
            api_key=settings.CLOUDINARY_API_KEY,
            api_secret=settings.CLOUDINARY_API_SECRET,
            secure=True,
        )
        CLOUDINARY_AVAILABLE = True
    else:
        CLOUDINARY_AVAILABLE = False
except Exception:
    CLOUDINARY_AVAILABLE = False


def find_image_file(image_filename: str) -> Path | None:
    """Find the local image file in images/ handling different extensions or minor naming differences."""
    if not IMAGES_DIR.is_dir():
        return None

    # 1. Exact match
    exact = IMAGES_DIR / image_filename
    if exact.is_file():
        return exact

    # 2. Match without extension and normalize suffixes like (1)
    target_clean = Path(image_filename).stem.lower().replace("-", "_").replace(" ", "_")
    for f in IMAGES_DIR.iterdir():
        if f.is_file():
            f_clean = f.stem.lower().replace("-", "_").replace(" ", "_").replace("(1)", "").replace("(2)", "").strip("_")
            if f_clean == target_clean or target_clean in f_clean or f_clean in target_clean:
                return f

    return None


def upload_image_to_cloudinary(image_filename: str, folder: str = "club-management/inventory") -> str | None:
    """Upload a local image file from images/ to Cloudinary. Returns secure_url or None."""
    if not CLOUDINARY_AVAILABLE:
        return None

    filepath = find_image_file(image_filename)
    if not filepath:
        return None

    try:
        public_id = f"eq_{filepath.stem}"
        response = cloudinary.uploader.upload(
            str(filepath),
            folder=folder,
            public_id=public_id,
            overwrite=True,
            resource_type="image",
        )
        url = response.get("secure_url")
        print(f"  ☁️ Uploaded {filepath.name} -> {url}")
        return url
    except Exception as e:
        print(f"  ⚠️ Cloudinary upload failed for {filepath.name}: {e}")
        return None


# 14 Diverse Equipment Definitions
EQUIPMENT_DATA: list[dict[str, Any]] = [
    {
        "name": "Raspberry Pi 4 Model B (4GB)",
        "category": EquipmentCategory.MICROCONTROLLER,
        "description": "Quad-core 64-bit ARM Cortex-A72 @ 1.5GHz, 4GB LPDDR4 RAM, Dual 4K Micro-HDMI display outputs, Gigabit Ethernet, USB 3.0, and onboard Wi-Fi / Bluetooth 5.0.",
        "total_quantity": 15,
        "available_quantity": 15,
        "storage_location": "Embedded Systems Lab, Shelf A-1",
        "image_file": "raspberry_pi_4.jpg",
        "fallback_image": "https://images.unsplash.com/photo-1553408227-108e3f4edef1?w=600&h=400&fit=crop",
    },
    {
        "name": "ESP32 NodeMCU Wi-Fi + Bluetooth Dev Board",
        "category": EquipmentCategory.MICROCONTROLLER,
        "description": "Dual-core Tensilica Xtensa 32-bit LX6 microprocessor, integrated 802.11 b/g/n Wi-Fi and Bluetooth 4.2 BLE, breadboard-friendly 30-pin header.",
        "total_quantity": 30,
        "available_quantity": 30,
        "storage_location": "IoT Lab, Rack 2",
        "image_file": "esp32_devkit.jpg",
        "fallback_image": "https://images.unsplash.com/photo-1518770660439-4636190af475?w=600&h=400&fit=crop",
    },
    {
        "name": "Rigol DS1054Z 50MHz Digital Oscilloscope",
        "category": EquipmentCategory.ELECTRONICS,
        "description": "4 Analog Channels, 50 MHz Bandwidth, 1 GSa/s Real-time sample rate, 24 Mpts Memory Depth, 7-inch WVGA color display with waveform playback.",
        "total_quantity": 8,
        "available_quantity": 8,
        "storage_location": "Circuits & Signal Lab, Bench 4",
        "image_file": "digital_oscilloscope.jpg",
        "fallback_image": "https://images.unsplash.com/photo-1581092160607-ee22621dd758?w=600&h=400&fit=crop",
    },
    {
        "name": "Fluke 117 True-RMS Digital Multimeter",
        "category": EquipmentCategory.ELECTRONICS,
        "description": "Professional-grade compact True-RMS digital multimeter with VoltAlert non-contact voltage detection, AutoVolt automatic AC/DC voltage selection, and min/max/average recording.",
        "total_quantity": 25,
        "available_quantity": 25,
        "storage_location": "Electronics Workbench, Cabinet B",
        "image_file": "digital_multimeter.jpg",
        "fallback_image": "https://images.unsplash.com/photo-1581092335397-9583eb92d232?w=400&h=300&fit=crop",
    },
    {
        "name": "Hakko FX-888D Digital Soldering Station",
        "category": EquipmentCategory.TOOLS_AND_HARDWARE,
        "description": "70W adjustable temperature soldering station (50°C - 480°C) with digital display, password locking, preset modes, and ceramic heating element for rapid thermal recovery.",
        "total_quantity": 12,
        "available_quantity": 12,
        "storage_location": "Hardware Fabrication Lab, Station 1",
        "image_file": "soldering_station.jpg",
        "fallback_image": "https://images.unsplash.com/photo-1581091226825-a6a2a5aee158?w=600&h=400&fit=crop",
    },
    {
        "name": "HC-SR04 Ultrasonic Distance Sensor Kit (10-Pack)",
        "category": EquipmentCategory.SENSOR_MODULE,
        "description": "Ultrasonic ranging module providing 2cm to 400cm non-contact measurement with 3mm precision. 5V operating voltage with trigger and echo logic pins.",
        "total_quantity": 20,
        "available_quantity": 20,
        "storage_location": "Sensors Bin 3, Drawer C",
        "image_file": "ultrasonic_sensor_kit.jpg",
        "fallback_image": "https://images.unsplash.com/photo-1518770660439-4636190af475?w=600&h=400&fit=crop",
    },
    {
        "name": "OV7670 VGA Camera Sensor Module with FIFO",
        "category": EquipmentCategory.SENSOR_MODULE,
        "description": "Compact 640x480 VGA CMOS camera module with integrated AL422B FIFO memory buffer, SCCB interface, and support for raw RGB, RGB565, and YUV422 formats.",
        "total_quantity": 18,
        "available_quantity": 18,
        "storage_location": "Vision & AI Lab, Shelf B-2",
        "image_file": "camera_sensor_module.jpg",
        "fallback_image": "https://images.unsplash.com/photo-1550751827-4bd374c3f58b?w=600&h=400&fit=crop",
    },
    {
        "name": "F450 Quadcopter Drone Frame & BLDC Motor Kit",
        "category": EquipmentCategory.ROBOTICS,
        "description": "450mm glass fiber quadcopter frame kit equipped with 4x 2212 920KV brushless motors, 30A SimonK ESCs, 1045 propellers, and integrated PCB power distribution board.",
        "total_quantity": 6,
        "available_quantity": 6,
        "storage_location": "UAV & Aero Lab, Locker 5",
        "image_file": "quadcopter_drone_kit.jpg",
        "fallback_image": "https://images.unsplash.com/photo-1508614589041-895b88991e3e?w=600&h=400&fit=crop",
    },
    {
        "name": "4-DOF Acrylic Robotic Arm Kit with Servo Motors",
        "category": EquipmentCategory.ROBOTICS,
        "description": "4-Degrees-of-Freedom mechanical robotic arm kit with 4x SG90 micro servo motors, laser-cut acrylic structural parts, and mechanical gripper claw.",
        "total_quantity": 10,
        "available_quantity": 10,
        "storage_location": "Robotics Workshop, Shelf R-4",
        "image_file": "robotic_arm_4dof.jpg",
        "fallback_image": "https://images.unsplash.com/photo-1485827404703-89b55fcc595e?w=600&h=400&fit=crop",
    },
    {
        "name": "Meta Quest 2 VR Headset (128GB)",
        "category": EquipmentCategory.COMPUTING_HARDWARE,
        "description": "Standalone VR headset with fast-switch LCD display (1832 x 1920 per eye), Snapdragon XR2 platform, 6DoF inside-out spatial tracking, and Touch controllers.",
        "total_quantity": 4,
        "available_quantity": 4,
        "storage_location": "XR & Metaverse Lab, Secure Vault 1",
        "image_file": "vr_headset.jpg",
        "fallback_image": "https://images.unsplash.com/photo-1622979135225-d2ba269bc1df?w=600&h=400&fit=crop",
    },
    {
        "name": "NVIDIA Jetson Nano Developer Kit (4GB B01)",
        "category": EquipmentCategory.COMPUTING_HARDWARE,
        "description": "128-core NVIDIA Maxwell GPU, Quad-core ARM A57 CPU @ 1.43 GHz, 4GB 64-bit LPDDR4, dual MIPI-CSI camera connectors, Gigabit Ethernet, and 472 GFLOPs AI computing power.",
        "total_quantity": 10,
        "available_quantity": 10,
        "storage_location": "AI Research Lab, Cabinet 1",
        "image_file": "nvidia_jetson_nano.jpg",
        "fallback_image": "https://images.unsplash.com/photo-1591488320449-011701bb6704?w=600&h=400&fit=crop",
    },
    {
        "name": "Cisco SG350-28P 28-Port Gigabit PoE Managed Switch",
        "category": EquipmentCategory.NETWORKING,
        "description": "28-Port Gigabit Ethernet managed switch with 24 PoE+ ports (195W power budget), 2 combo mini-GBIC SFP slots, Layer 3 traffic management, and advanced network security.",
        "total_quantity": 5,
        "available_quantity": 5,
        "storage_location": "Network Operations Center, Server Rack 2",
        "image_file": "gigabit_managed_switch.jpg",
        "fallback_image": "https://images.unsplash.com/photo-1544197150-b99a580bb7a8?w=600&h=400&fit=crop",
    },
    {
        "name": "Rode Wireless GO II Dual Channel Microphone System",
        "category": EquipmentCategory.AUDIO_VISUAL,
        "description": "Dual-channel wireless microphone system with built-in omnidirectional condenser capsules, 200m line-of-sight range, onboard recording (over 40 hours), and USB-C / 3.5mm analog outputs.",
        "total_quantity": 6,
        "available_quantity": 6,
        "storage_location": "AV Studio, Cabinet AV-1",
        "image_file": "wireless_collar_mic.jpg",
        "fallback_image": "https://images.unsplash.com/photo-1590602847861-f357a9332bbc?w=600&h=400&fit=crop",
    },
    {
        "name": "Precision 3D Printer Maintenance & Tool Set",
        "category": EquipmentCategory.TOOLS_AND_HARDWARE,
        "description": "Comprehensive 3D printer kit with hardened steel MK8 nozzles (0.2 - 1.0mm), PTFE tube cutter, deburring tool, scraper, digital caliper, cleaning needles, and hex wrenches.",
        "total_quantity": 14,
        "available_quantity": 14,
        "storage_location": "Rapid Prototyping Lab, Drawer T-2",
        "image_file": "creality_3d_printer_toolset.jpg",
        "fallback_image": "https://images.unsplash.com/photo-1581092160607-ee22621dd758?w=600&h=400&fit=crop",
    },
]


def seed_equipment(db: Session) -> None:
    """Seed all 14 equipment items into the database."""
    print("🚀 Starting equipment seeding...")

    for eq_data in EQUIPMENT_DATA:
        name = eq_data["name"]

        # Check if image exists locally in images/ and upload to Cloudinary
        image_url = upload_image_to_cloudinary(eq_data["image_file"])
        if not image_url:
            image_url = eq_data["fallback_image"]

        # Check existing equipment by name
        existing = db.scalar(select(Equipment).where(Equipment.name == name))
        if existing:
            print(f"  🔄 Updating existing equipment: {name}")
            existing.category = eq_data["category"]
            existing.description = eq_data["description"]
            existing.total_quantity = eq_data["total_quantity"]
            existing.available_quantity = eq_data["available_quantity"]
            existing.storage_location = eq_data["storage_location"]
            if image_url:
                existing.equipment_image_url = image_url
        else:
            print(f"  ✨ Creating new equipment: {name}")
            new_eq = Equipment(
                name=name,
                category=eq_data["category"],
                description=eq_data["description"],
                total_quantity=eq_data["total_quantity"],
                available_quantity=eq_data["available_quantity"],
                storage_location=eq_data["storage_location"],
                equipment_image_url=image_url,
            )
            db.add(new_eq)

    try:
        db.commit()
        print("✅ Equipment seeding completed successfully!")
    except Exception as e:
        db.rollback()
        print(f"❌ Error committing equipment seed: {e}")
        raise


def main() -> None:
    db = SessionLocal()
    try:
        seed_equipment(db)
    finally:
        db.close()


if __name__ == "__main__":
    main()
