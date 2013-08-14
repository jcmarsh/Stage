/*
Copyright (c) 2007, Geoff Biggs
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

    * Redistributions of source code must retain the above copyright notice,
      this list of conditions and the following disclaimer.
    * Redistributions in binary form must reproduce the above copyright notice,
      this list of conditions and the following disclaimer in the documentation
      and/or other materials provided with the distribution.
    * Neither the name of the Player Project nor the names of its contributors
      may be used to endorse or promote products derived from this software
      without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR
ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
*/

/*
 * This file declares a C client library proxy for the interface. The functions
 * are defined in eginterf_client.c.
 */

#ifdef __cplusplus
extern "C" {
#endif

#define SMRTLN_EXPORT

  typedef struct
  {
    /* Device info; must be at the start of all device structures. */
    playerc_device_t info;

  } smrtlninterf_t;

  SMRTLN_EXPORT smrtlninterf_t *smrtlninterf_create (playerc_client_t *client, int index);

  SMRTLN_EXPORT void smrtlninterf_destroy (smrtlninterf_t *device);

  SMRTLN_EXPORT int smrtlninterf_subscribe (smrtlninterf_t *device, int access);

  SMRTLN_EXPORT int smrtlninterf_unsubscribe (smrtlninterf_t *device);

  SMRTLN_EXPORT int smrtlninterf_set_param (smrtlninterf_t *device, int index, double value);

  SMRTLN_EXPORT int smrtlninterf_sup_sensor (smrtlninterf_t *device, int index, int state);

#ifdef __cplusplus
}
#endif
