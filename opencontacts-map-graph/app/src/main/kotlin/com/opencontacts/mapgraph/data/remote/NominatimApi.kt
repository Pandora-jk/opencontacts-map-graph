package com.opencontacts.mapgraph.data.remote

import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import okhttp3.OkHttpClient
import okhttp3.HttpUrl.Companion.toHttpUrl
import java.util.concurrent.TimeUnit

/**
 * Nominatim (OpenStreetMap) geocoding service.
 * Implements rate limiting to comply with Nominatim usage policy.
 * https://operations.osmfoundation.org/policies/nominatim/
 */
class NominatimApi(
    private val userAgent: String = "OpenContactsMapGraph/1.0",
    private val rateLimitMs: Long = 1000L // 1 request per second minimum
) {
    private val client = OkHttpClient.Builder()
        .connectTimeout(10, TimeUnit.SECONDS)
        .readTimeout(10, TimeUnit.SECONDS)
        .build()
    
    private var lastRequestTime = 0L
    
    /**
     * Geocode an address string to coordinates.
     * Returns latitude, longitude pair or null if not found.
     */
    suspend fun geocodeAddress(
        query: String,
        country: String? = null
    ): Result<Coordinates?> = withContext(Dispatchers.IO) {
        try {
            enforceRateLimit()
            
            val searchQuery = buildString {
                append(query.trim())
                if (country != null) {
                    append(", ")
                    append(country)
                }
            }
            
            val url = "https://nominatim.openstreetmap.org/search".toHttpUrl()
                .newBuilder()
                .addQueryParameter("q", searchQuery)
                .addQueryParameter("format", "json")
                .addQueryParameter("limit", "1")
                .addQueryParameter("addressdetails", "0")
                .build()
            
            val request = okhttp3.Request.Builder()
                .url(url)
                .header("User-Agent", userAgent)
                .build()
            
            client.newCall(request).execute().use { response ->
                if (!response.isSuccessful) {
                    return@withContext Result.failure(ApiException("HTTP ${response.code}"))
                }
                
                val body = response.body?.string()
                if (body == null || body == "[]" || body.trim() == "[]") {
                    return@withContext Result.success(null)
                }
                
                // Parse JSON manually to avoid extra dependencies
                val lat = parseJsonField(body, "lat")?.toDoubleOrNull()
                val lon = parseJsonField(body, "lon")?.toDoubleOrNull()
                
                if (lat != null && lon != null) {
                    Result.success(Coordinates(lat, lon))
                } else {
                    Result.success(null)
                }
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
    /**
     * Batch geocode multiple addresses.
     * Respects rate limiting between requests.
     */
    suspend fun geocodeBatch(
        addresses: List<String>,
        country: String? = null
    ): Map<String, Result<Coordinates?>> = withContext(Dispatchers.IO) {
        val results = mutableMapOf<String, Result<Coordinates?>>()
        
        addresses.forEach { address ->
            val result = geocodeAddress(address, country)
            results[address] = result
        }
        
        results
    }
    
    private suspend fun enforceRateLimit() = withContext(Dispatchers.IO) {
        val now = System.currentTimeMillis()
        val timeSinceLastRequest = now - lastRequestTime
        if (timeSinceLastRequest < rateLimitMs) {
            kotlinx.coroutines.delay(rateLimitMs - timeSinceLastRequest)
        }
        lastRequestTime = System.currentTimeMillis()
    }
    
    private fun parseJsonField(json: String, field: String): String? {
        val pattern = "\"$field\"\\s*:\\s*\"([^\"]+)\""
        val regex = Regex(pattern)
        return regex.find(json)?.groupValues?.get(1)
    }
    
    data class Coordinates(
        val latitude: Double,
        val longitude: Double
    )
    
    class ApiException(message: String) : Exception(message)
}
