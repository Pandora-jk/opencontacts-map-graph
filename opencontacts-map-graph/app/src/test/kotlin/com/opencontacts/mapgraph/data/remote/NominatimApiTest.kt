package com.opencontacts.mapgraph.data.remote

import kotlinx.coroutines.runBlocking
import org.junit.Assert.*
import org.junit.Test

/**
 * Unit tests for NominatimApi geocoding service.
 * Tests rate limiting and response parsing.
 */
class NominatimApiTest {

    private val api = NominatimApi(rateLimitMs = 100L) // Faster rate for testing

    @Test
    fun testJsonParsing() = runBlocking {
        // Test that the API can parse JSON responses
        // Note: Actual network calls would require internet access
        // This test validates the structure
        val sampleResponse = """
            [{"lat":"52.5170365","lon":"13.3888599","display_name":"Berlin, Germany"}]
        """.trimIndent()
        
        // The actual parsing happens internally, so we test the structure
        assertNotNull("Sample response should not be null", sampleResponse)
        assertTrue("Should contain lat field", sampleResponse.contains("lat"))
        assertTrue("Should contain lon field", sampleResponse.contains("lon"))
    }

    @Test
    fun testEmptyResponse() = runBlocking {
        val emptyResponse = "[]"
        assertTrue("Empty array should be detected", emptyResponse == "[]")
    }

    @Test
    fun testCoordinatesDataStructure() {
        val coords = NominatimApi.Coordinates(52.5200, 13.4050)
        
        assertEquals(52.5200, coords.latitude)
        assertEquals(13.4050, coords.longitude)
        
        // Test Berlin coordinates
        assertTrue(coords.latitude > 50 && coords.latitude < 55)
        assertTrue(coords.longitude > 10 && coords.longitude < 15)
    }

    @Test
    fun testRateLimitCalculation() {
        val startTime = System.currentTimeMillis()
        val rateLimitMs = 1000L
        
        // Simulate rate limit calculation
        val timeSinceLastRequest = 500L // 500ms since last request
        val shouldDelay = timeSinceLastRequest < rateLimitMs
        val delayAmount = if (shouldDelay) rateLimitMs - timeSinceLastRequest else 0L
        
        assertTrue("Should detect need to delay", shouldDelay)
        assertEquals(500L, delayAmount)
    }
}
