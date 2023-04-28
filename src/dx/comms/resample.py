import structlog

from dx.filtering import handle_resample
from dx.types.filters import DEXResampleMessage

logger = structlog.get_logger(__name__)


# ref: https://jupyter-notebook.readthedocs.io/en/stable/comms.html#opening-a-comm-from-the-frontend
def resampler(comm, open_msg):
    """
    Datalink resample request.
    """

    @comm.on_msg
    def _recv(msg):
        # Is separate function to make testing easier.
        handle_resample_comm(msg)

    comm.send({"status": "connected", "source": "resampler"})


def handle_resample_comm(msg):
    data = msg.get("content", {}).get("data", {})
    if not data:
        return

    if "display_id" in data and "filters" in data:
        msg = DEXResampleMessage.parse_obj(data)
        handle_resample(msg)
