from aiogram.filters.callback_data import CallbackData


class TargetCallbackFactory(CallbackData, prefix="target"):
    target: int


class ZoneCallbackFactory(CallbackData, prefix="zone"):
    zone: str

class WorkTypeCallbackFactory(CallbackData, prefix="work_type"):
    work_type: str

class PhotoCallbackFactory(CallbackData, prefix="object_photo"):
    action: str


class WorkerNotificationCallbackFactory(CallbackData, prefix="worker_notification"):
    action: str


class WorkerProfileConfirmationCallbackFactory(CallbackData, prefix="w_p_c"):
    action: str


class WorkerControlsCallBackFactory(CallbackData, prefix="w_c"):
    control: str
    action: str
    object_id: int = 0


class WorkerBackCallBackFactory(CallbackData, prefix="w_back"):
    destination: str


class WorkerMainSectionsCallBackFactory(CallbackData, prefix="w_menu"):
    destination: str


class WorkerPagesSectionsCallBackFactory(CallbackData, prefix="w_pages"):
    destination: str
    page: int = 1


class WorkerDetailsCallBackFactory(CallbackData, prefix="w_details"):
    object_name: str
    object_id: int


class WorkerRedirectDetailsCallBackFactory(CallbackData, prefix="w_r_d"):
    redirect: str
    object_name: str
    object_id: int


class AdminControlsCallBackFactory(CallbackData, prefix="a"):
    target: str
    action: str
    object_id: int
    

class EmployerBackCallBackFactory(CallbackData, prefix="e_back"):
    destination: str


class EmployerControlsCallBackFactory(CallbackData, prefix="e_c"):
    control: str
    action: str
    object_id: int = 0


class EmployerMainSectionsCallBackFactory(CallbackData, prefix="e_menu"):
    destination: str


class EmployerPagesSectionsCallBackFactory(CallbackData, prefix="e_pages"):
    destination: str
    page: int = 1


class EmployerDetailsCallBackFactory(CallbackData, prefix="e_details"):
    object_name: str
    object_id: int


class EmployerRedirectDetailsCallBackFactory(CallbackData, prefix="e_r_d"):
    redirect: str
    object_name: str
    object_id: int
    