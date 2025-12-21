from core.camera_manager.camera_manager import CameraManager
from core.seedo_manager import SeeDoManager
from core.ml.ml_manager import ML_manager
from core.seedo.seedo import SemanticSimilaritySeeDo
from core.seedo.schemas import SeeDoSchema, SemanticRegion, SemanticSimilarityConfigSchema, ActionSchema, EmailActionConfig
from core.seedo.action import EmailAction
import time
from PIL import Image
import numpy as np
from core.secrets import get_secret





class AppController:
    """
    Central orchestrator for backend operations.
    Called by the UI tick loop to update camera, recording, SeeDo evaluations.
    UI never directly interacts with core modules — it only calls controller methods.
    """

    def __init__(self):
        self.ml_manager = ML_manager()
        self.camera_manager = CameraManager()
        self.seedo_manager = SeeDoManager(self.ml_manager, self.camera_manager)

        #NOTE: I could see lazy loading of models being better if there are many models
        # and a given model is not used by any SeeDo instances yet.
        seedo_types_loaded = [seedo.type for seedo in self.seedo_manager.seedos]
        # if 'semantic_similarity' in seedo_types_loaded:
        #     self.ml_manager.Load_MobileNetV3()
        # if 'distance_change' in seedo_types_loaded:
        #     self.ml_manager.Load_DepthAnythingV2()
        
        # But we would need to load the models to use them for previews. So, maybe no lazy loading? This
        # will become an issue if 
        self.ml_manager.Load_DepthAnythingV2()
        self.ml_manager.Load_MobileNetV3()

        self.new_seedo_created = False

    def tick(self):
        """Heartbeat invoked by UI .after() loop."""
        if self.camera_manager.active:
            self.camera_manager.capture_frame()
            self.camera_manager.clear_old_videos()
            # Is this using the old frame and running it twice?
            self.seedo_manager.run(self.camera_manager.latest_frame, time.time())
    # -------- SEEDO CONTROL ---------

    def toggle_seedo(self, seedo_name):
        self.seedo_manager.toggle_seedo(seedo_name) 

    def new_seedo_handled(self):
        self.new_seedo_created = False
        
    def create_semantic_similarity_seedo(self, options_data) -> bool:
        """Create and add a new Semantic Similarity SeeDo with given options.
        If the options are invalid raise a ValueError. and return False."""
       
        semantic_regions = []

        for idx, (roi, image, emb) in enumerate(options_data['semantic_regions']):
            image_path = SemanticSimilaritySeeDo.save_roi_image_to_file(
                options_data['name'],
                image,
                idx
            )
            embedding_path = SemanticSimilaritySeeDo.save_roi_embedding_to_file(
                options_data['name'],
                idx,
                emb
            )
            new_region = SemanticRegion(
                image=image,
                embedding=emb,
                roi=roi,
                image_path=image_path,
                embedding_path=embedding_path,
                similarity_threshold=options_data['similarity_threshold'],
                greater_than=True if options_data['trigger_when'] == 'greater' else False
            )
            semantic_regions.append(new_region)

        # TODO: this only works with a email action. This should be
        # more universal.
       
        email_action_config = EmailActionConfig(
            to=options_data['email_to'],
            from_ = get_secret('FROM_EMAIL'),
            body_template = options_data['email_body'],
            subject = 'Semantic Seedo Triggered'
        )

        action = EmailAction(email_action_config)

        schema = SeeDoSchema(
            type='semantic',
            name=options_data['name'],
            interval_sec=options_data['trigger_interval_sec'],
            min_retrigger_interval_sec=options_data['min_retrigger_interval_sec'],
            enabled=False,
            action=ActionSchema(type='email', params=email_action_config.model_dump()),
            config=SemanticSimilarityConfigSchema(semantic_regions=semantic_regions).model_dump()
        )

        semantic_seedo = SemanticSimilaritySeeDo.from_schema(schema, SemanticSimilarityConfigSchema(semantic_regions=semantic_regions), action)
        self.seedo_manager.save_seedo(semantic_seedo)

        self.seedo_manager.add(semantic_seedo)

        self.new_seedo_created = True



    # -------- CAMERA CONTROL --------
    def is_camera_active(self) -> bool:
        return self.camera_manager.active

    def start_camera(self):
        print("Starting camera...")
        self.camera_manager.active = True

    def stop_camera(self):
        print("Stopping camera...")
        self.camera_manager.active = False

    def get_latest_frame(self) -> np.ndarray | None:
        return self.camera_manager.latest_frame

    # -------- RECORDING CONTROL --------
    def start_recording(self):
        print("Recording enabled")
        self.camera_manager.saving = True

    def stop_recording(self):
        print("Recording disabled")
        self.camera_manager.saving = False

    # -------- ML CONTROL --------
    def get_embedding(self, imgs: list[Image.Image]) -> np.ndarray:
        """Get embedding from ML model for given image."""
        return self.ml_manager.mobile_net_v3.get_embedding(imgs)
    
    def start_running_depth_map(self):
        if self.ml_manager.depth_anything_v2_vits_378:
            self.ml_manager.depth_anything_v2_vits_378.start_running_depth_map()
    
    def stop_running_depth_map(self):
        if self.ml_manager.depth_anything_v2_vits_378:
            self.ml_manager.depth_anything_v2_vits_378.stop_running_depth_map()
   
    
    def request_depth(self):
        if self.ml_manager.depth_anything_v2_vits_378:
            self.ml_manager.depth_anything_v2_vits_378.request_depth(self.get_latest_frame())

    def get_depth_map_gray_scale(self):
        dm = self.ml_manager.depth_anything_v2_vits_378

        if dm is None:
            return None

        if dm.last_depth_map is None:
            return None

        return dm.raw_to_gray_scale(dm.last_depth_map)

    

    # -------- SHUTDOWN --------
    def shutdown(self):
        """Gracefully stop camera, recorder, and release hardware."""
        print("Controller shutdown")
        self.camera_manager.active = False
        self.camera_manager.saving = False
        self.camera_manager.release()
