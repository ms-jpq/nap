from typing import AsyncIterator

from ...lsp.requests.completion import request
from ...shared.runtime import Supervisor
from ...shared.runtime import Worker as BaseWorker
from ...shared.settings import BaseClient
from ...shared.types import Completion, Context
from ..cache.worker import CacheWorker


class Worker(BaseWorker[BaseClient, None], CacheWorker):
    def __init__(self, supervisor: Supervisor, options: BaseClient, misc: None) -> None:
        CacheWorker.__init__(self, supervisor=supervisor)
        BaseWorker.__init__(self, supervisor=supervisor, options=options, misc=misc)
        self._only_use_cached = False

    async def work(self, context: Context) -> AsyncIterator[Completion]:
        only_use_cached = self._only_use_cached

        can_use, cached = await self._use_cache(context, limit=self._options.limit)
        async for c in cached:
            yield c

        if only_use_cached and can_use:
            pass
        else:
            stream = request(
                self._supervisor.nvim,
                short_name=self._options.short_name,
                tie_breaker=self._options.tie_breaker,
                context=context,
            )

            async for only_use_cached, comps in stream:
                self._only_use_cached = only_use_cached
                for c in comps:
                    yield c
                await self._set_cache(context, completions=comps)

